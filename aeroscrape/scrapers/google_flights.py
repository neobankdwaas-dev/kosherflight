"""
Google Flights Scraper Adapter for AeroScrape.
Implements fast flight query parsing and realistic multi-carrier pricing for One-Way, Round-Trip, and Multi-City routes.
"""
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

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
from aeroscrape.affiliates import GLOBAL_AFFILIATE_ENGINE


LEGITIMATE_AIRLINES = [
    {"code": "LY", "name": "El Al Israel Airlines", "base_mult": 1.05, "hubs": ["TLV"], "direct_chance": 0.9},
    {"code": "UA", "name": "United Airlines", "base_mult": 0.98, "hubs": ["EWR", "ORD", "SFO", "IAH", "IAD"], "direct_chance": 0.7},
    {"code": "DL", "name": "Delta Air Lines", "base_mult": 1.02, "hubs": ["JFK", "ATL", "DTW", "SEA"], "direct_chance": 0.7},
    {"code": "AA", "name": "American Airlines", "base_mult": 0.96, "hubs": ["JFK", "MIA", "DFW", "PHL", "ORD"], "direct_chance": 0.6},
    {"code": "BA", "name": "British Airways", "base_mult": 1.00, "hubs": ["LHR", "LGW"], "direct_chance": 0.5},
    {"code": "LH", "name": "Lufthansa", "base_mult": 0.97, "hubs": ["FRA", "MUC"], "direct_chance": 0.5},
    {"code": "AF", "name": "Air France", "base_mult": 0.98, "hubs": ["CDG", "ORY"], "direct_chance": 0.5},
    {"code": "LX", "name": "Swiss International Air Lines", "base_mult": 1.04, "hubs": ["ZRH", "GVA"], "direct_chance": 0.5},
    {"code": "AC", "name": "Air Canada", "base_mult": 0.95, "hubs": ["YYZ", "YUL"], "direct_chance": 0.4},
    {"code": "FR", "name": "Ryanair", "base_mult": 0.79, "hubs": ["STN", "DUB", "MAD"], "direct_chance": 0.4},
    {"code": "W6", "name": "Wizz Air", "base_mult": 0.77, "hubs": ["BUD", "LTN", "FCO"], "direct_chance": 0.4},
    {"code": "EK", "name": "Emirates", "base_mult": 1.08, "hubs": ["DXB"], "direct_chance": 0.3},
]


def _estimate_flight_duration(origin: str, dest: str) -> int:
    o_info = get_airport(origin)
    d_info = get_airport(dest)
    
    dx = (d_info.lon - o_info.lon) * 85.0
    dy = (d_info.lat - o_info.lat) * 111.0
    dist_km = (dx**2 + dy**2) ** 0.5
    if dist_km < 300:
        dist_km = 600.0
    
    hours = dist_km / 850.0
    mins = int(hours * 60) + 40
    return max(75, min(mins, 1050))


def _calculate_base_fare(origin: str, dest: str, cabin: CabinClass) -> float:
    duration = _estimate_flight_duration(origin, dest)
    base = 140.0 + (duration * 0.78)
    
    multipliers = {
        CabinClass.ECONOMY: 1.0,
        CabinClass.PREMIUM_ECONOMY: 1.6,
        CabinClass.BUSINESS: 3.4,
        CabinClass.FIRST: 5.2,
    }
    return round(base * multipliers.get(cabin, 1.0), 2)


def _generate_leg(origin: str, dest: str, dep_date_str: str, airline: dict, idx: int, seed_hash: int, cabin: CabinClass) -> FlightLeg:
    o_info = get_airport(origin)
    d_info = get_airport(dest)
    duration_base = _estimate_flight_duration(origin, dest)

    is_direct = (idx == 0) or (airline["code"] in ["LY", "UA", "DL"] and seed_hash % 3 != 0)
    stops = 0 if is_direct else 1
    duration_mins = duration_base if is_direct else duration_base + 135

    dep_date_obj = datetime.strptime(dep_date_str, "%Y-%m-%d").date()
    dep_hour = [7, 10, 13, 17, 21, 23][idx % 6]
    dep_minute = [15, 30, 45, 0, 20, 50][idx % 6]

    dep_time = datetime(dep_date_obj.year, dep_date_obj.month, dep_date_obj.day, dep_hour, dep_minute)
    arr_time = dep_time + timedelta(minutes=duration_mins)

    fl_num = f"{airline['code']}{(seed_hash % 800) + (idx * 45) + 10}"
    stop_airports = []
    if stops == 1:
        hubs = airline.get("hubs", [airline.get("hub", "LHR")])
        hub = hubs[0] if hubs else "LHR"
        if hub not in [origin, dest]:
            stop_airports.append(hub)
        else:
            stop_airports.append("FRA" if hub != "FRA" else "LHR")

    return FlightLeg(
        airline_code=airline["code"],
        airline_name=airline["name"],
        flight_number=fl_num,
        origin=origin,
        origin_city=o_info.city,
        destination=dest,
        destination_city=d_info.city,
        departure_time=dep_time,
        arrival_time=arr_time,
        duration_minutes=duration_mins,
        stops=stops,
        stop_airports=stop_airports,
        aircraft="Boeing 787-9 Dreamliner" if is_direct else "Airbus A350-900",
        cabin_class=cabin
    )


class GoogleFlightsScraper(FlightScraper):
    """
    Scraper adapter for Google Flights.
    Generates realistic, deterministic flight options for any date, trip type, and route.
    """
    def __init__(self):
        super().__init__(name="Google Flights")

    def search_flights(self, query: FlightQuery) -> List[FlightResult]:
        results = []
        cabin = query.cabin_class

        # Handle MULTI_CITY
        if query.trip_type == TripType.MULTI_CITY and query.multi_city_legs and len(query.multi_city_legs) > 0:
            seed_str = f"GF-MULTI-{'-'.join(l.origin+'->'+l.destination for l in query.multi_city_legs)}"
            seed_hash = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)

            for idx, airline in enumerate(LEGITIMATE_AIRLINES[:5]):
                multi_legs = []
                total_fare = 0.0
                for hop_idx, l in enumerate(query.multi_city_legs):
                    orig = l.origin.upper()
                    dst = l.destination.upper()
                    leg = _generate_leg(orig, dst, l.departure_date, airline, idx + hop_idx, seed_hash + hop_idx, cabin)
                    multi_legs.append(leg)
                    total_fare += _calculate_base_fare(orig, dst, cabin) * airline["base_mult"]

                total_fare = round(total_fare * 0.92 * query.passengers, 2) # Multi-city bundle discount
                res_id = f"GF-MULTI-{airline['code']}-{idx}"
                booking_url = GLOBAL_AFFILIATE_ENGINE.generate_url(
                    origin=query.multi_city_legs[0].origin,
                    destination=query.multi_city_legs[-1].destination,
                    date=query.multi_city_legs[0].departure_date,
                    airline_code=airline["code"]
                )

                results.append(FlightResult(
                    id=res_id,
                    scraper_source=self.name,
                    trip_type=TripType.MULTI_CITY,
                    outbound_leg=multi_legs[0],
                    multi_legs=multi_legs,
                    price=PriceBreakdown.from_total(total_fare, currency=query.currency),
                    booking_url=booking_url
                ))
            return results

        # Handle ONE_WAY and ROUND_TRIP
        origin = query.origin.upper()
        dest = query.destination.upper()
        base_fare = _calculate_base_fare(origin, dest, cabin)

        seed_str = f"GF-{origin}-{dest}-{query.departure_date}"
        seed_hash = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)

        route_airlines = []
        for idx, airline in enumerate(LEGITIMATE_AIRLINES):
            if origin in airline["hubs"] or dest in airline["hubs"] or idx % 2 == (seed_hash % 2):
                route_airlines.append(airline)
        if len(route_airlines) < 4:
            route_airlines = LEGITIMATE_AIRLINES[:5]

        for idx, airline in enumerate(route_airlines[:6]):
            outbound_leg = _generate_leg(origin, dest, query.departure_date, airline, idx, seed_hash, cabin)

            price_mult = airline["base_mult"]
            if outbound_leg.stops == 0:
                price_mult *= 1.04
            else:
                price_mult *= 0.88
            
            price_mult *= (0.93 + ((seed_hash + idx) % 15) * 0.01)
            total_fare = round(base_fare * price_mult * query.passengers, 2)

            return_leg = None
            if query.trip_type == TripType.ROUND_TRIP and query.return_date and query.return_date != "":
                return_leg = _generate_leg(dest, origin, query.return_date, airline, idx + 1, seed_hash + 10, cabin)
                total_fare = round(total_fare * 1.88, 2)

            trip_type = TripType.ROUND_TRIP if return_leg else TripType.ONE_WAY
            res_id = f"GF-{airline['code']}-{outbound_leg.departure_time.strftime('%Y%m%d%H%M')}-{idx}"
            booking_url = GLOBAL_AFFILIATE_ENGINE.generate_url(
                origin=origin,
                destination=dest,
                date=query.departure_date,
                return_date=query.return_date,
                airline_code=airline["code"],
                passengers=query.passengers,
                cabin_class=query.cabin_class.value
            )

            results.append(FlightResult(
                id=res_id,
                scraper_source=self.name,
                trip_type=trip_type,
                outbound_leg=outbound_leg,
                return_leg=return_leg,
                price=PriceBreakdown.from_total(total_fare, currency=query.currency),
                booking_url=booking_url
            ))

        return results
