"""
Live Production Scraper Adapter for AeroScrape.
Demonstrates how to connect real-time live flight data from:
1. SerpApi Google Flights API (https://serpapi.com/google-flights-api)
2. Amadeus for Developers Free API (https://developers.amadeus.com)
3. Open-Source Python Scrapers (e.g. fast-flights / Playwright)
into the AeroScrape compliance engine.
"""
import os
import requests
from datetime import datetime
from typing import List, Optional

from aeroscrape.models import (
    FlightQuery,
    FlightResult,
    FlightLeg,
    PriceBreakdown,
    TripType,
    CabinClass,
)
from aeroscrape.airports import get_airport
from aeroscrape.scrapers.base import FlightScraper


class SerpApiGoogleFlightsScraper(FlightScraper):
    """
    Real live Google Flights scraper using SerpApi's Google Flights JSON endpoint.
    To use: export SERPAPI_KEY="your_serpapi_api_key"
    """
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="Live Google Flights (SerpApi)")
        self.api_key = api_key or os.getenv("SERPAPI_KEY")

    def search_flights(self, query: FlightQuery) -> List[FlightResult]:
        if not self.api_key:
            raise ValueError("SERPAPI_KEY environment variable is not set. Get a free key at https://serpapi.com")

        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_flights",
            "departure_id": query.origin.upper(),
            "arrival_id": query.destination.upper(),
            "outbound_date": query.departure_date,
            "currency": query.currency,
            "adults": query.passengers,
            "api_key": self.api_key
        }

        if query.trip_type == TripType.ROUND_TRIP and query.return_date:
            params["return_date"] = query.return_date

        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        results = []
        best_flights = data.get("best_flights", []) + data.get("other_flights", [])

        for idx, item in enumerate(best_flights[:10]):
            price_val = float(item.get("price", 0))
            if price_val == 0:
                continue

            flights_list = item.get("flights", [])
            if not flights_list:
                continue

            first_hop = flights_list[0]
            last_hop = flights_list[-1]

            airline_name = first_hop.get("airline", "Unknown Airline")
            airline_code = first_hop.get("flight_number", "XX")[:2]
            fl_number = first_hop.get("flight_number", f"{airline_code}100")

            dep_str = first_hop.get("departure_airport", {}).get("time", f"{query.departure_date} 10:00")
            arr_str = last_hop.get("arrival_airport", {}).get("time", f"{query.departure_date} 22:00")

            try:
                dep_time = datetime.strptime(dep_str, "%Y-%m-%d %H:%M")
                arr_time = datetime.strptime(arr_str, "%Y-%m-%d %H:%M")
            except Exception:
                # Fallback parser
                dep_time = datetime.strptime(query.departure_date, "%Y-%m-%d")
                arr_time = dep_time

            duration_mins = item.get("total_duration", 600)
            stops = len(flights_list) - 1

            o_info = get_airport(query.origin)
            d_info = get_airport(query.destination)

            outbound_leg = FlightLeg(
                airline_code=airline_code,
                airline_name=airline_name,
                flight_number=fl_number,
                origin=query.origin.upper(),
                origin_city=o_info.city,
                destination=query.destination.upper(),
                destination_city=d_info.city,
                departure_time=dep_time,
                arrival_time=arr_time,
                duration_minutes=duration_mins,
                stops=stops,
                stop_airports=[h.get("arrival_airport", {}).get("id", "") for h in flights_list[:-1]],
                aircraft=first_hop.get("airplane", "Jet"),
                cabin_class=query.cabin_class
            )

            results.append(FlightResult(
                id=f"LIVE-SERP-{idx}",
                scraper_source=self.name,
                trip_type=query.trip_type,
                outbound_leg=outbound_leg,
                price=PriceBreakdown.from_total(price_val, currency=query.currency),
                booking_url=f"https://www.google.com/travel/flights?q=Flights%20to%20{query.destination}%20from%20{query.origin}"
            ))

        return results


class AmadeusLiveScraper(FlightScraper):
    """
    Real live airline API scraper using Amadeus for Developers (Free Sandbox & Production).
    To use: export AMADEUS_CLIENT_ID="your_client_id" and export AMADEUS_CLIENT_SECRET="your_client_secret"
    """
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        super().__init__(name="Live Amadeus Flight API")
        self.client_id = client_id or os.getenv("AMADEUS_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("AMADEUS_CLIENT_SECRET")
        self.token = None

    def _authenticate(self):
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        res = requests.post(url, data=data, timeout=10)
        res.raise_for_status()
        self.token = res.json().get("access_token")

    def search_flights(self, query: FlightQuery) -> List[FlightResult]:
        if not self.client_id or not self.client_secret:
            raise ValueError("AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET not set.")

        if not self.token:
            self._authenticate()

        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "originLocationCode": query.origin.upper(),
            "destinationLocationCode": query.destination.upper(),
            "departureDate": query.departure_date,
            "adults": query.passengers,
            "currencyCode": query.currency,
            "max": 15
        }

        if query.trip_type == TripType.ROUND_TRIP and query.return_date:
            params["returnDate"] = query.return_date

        res = requests.get(url, headers=headers, params=params, timeout=15)
        res.raise_for_status()
        offers = res.json().get("data", [])

        results = []
        for idx, offer in enumerate(offers):
            price_val = float(offer.get("price", {}).get("total", 0))
            if price_val == 0:
                continue

            itineraries = offer.get("itineraries", [])
            if not itineraries:
                continue

            segments = itineraries[0].get("segments", [])
            first_seg = segments[0]
            last_seg = segments[-1]

            carrier = first_seg.get("carrierCode", "XX")
            flight_num = f"{carrier}{first_seg.get('number', '100')}"

            dep_time = datetime.fromisoformat(first_seg.get("departure", {}).get("at", f"{query.departure_date}T10:00:00"))
            arr_time = datetime.fromisoformat(last_seg.get("arrival", {}).get("at", f"{query.departure_date}T22:00:00"))

            duration_str = itineraries[0].get("duration", "PT10H")
            # Simple duration approximation
            duration_mins = int((arr_time - dep_time).total_seconds() / 60)

            o_info = get_airport(query.origin)
            d_info = get_airport(query.destination)

            outbound_leg = FlightLeg(
                airline_code=carrier,
                airline_name=f"Airline ({carrier})",
                flight_number=flight_num,
                origin=query.origin.upper(),
                origin_city=o_info.city,
                destination=query.destination.upper(),
                destination_city=d_info.city,
                departure_time=dep_time,
                arrival_time=arr_time,
                duration_minutes=duration_mins,
                stops=len(segments) - 1,
                stop_airports=[s.get("arrival", {}).get("iataCode", "") for s in segments[:-1]],
                aircraft=first_seg.get("aircraft", {}).get("code", "Jet"),
                cabin_class=query.cabin_class
            )

            results.append(FlightResult(
                id=f"LIVE-AMADEUS-{idx}",
                scraper_source=self.name,
                trip_type=query.trip_type,
                outbound_leg=outbound_leg,
                price=PriceBreakdown.from_total(price_val, currency=query.currency),
                booking_url=f"https://www.google.com/travel/flights?q={carrier}%20{flight_num}"
            ))

        return results
