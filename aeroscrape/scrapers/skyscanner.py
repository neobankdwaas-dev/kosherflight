"""
Skyscanner & OTA Aggregator Scraper Adapter for AeroScrape.
Supports One-Way, Round-Trip, and Multi-City trip types.
"""
import hashlib
from datetime import datetime, timedelta
from typing import List

from aeroscrape.models import (
    FlightQuery,
    FlightResult,
    FlightLeg,
    PriceBreakdown,
    TripType,
)
from aeroscrape.airports import get_airport
from aeroscrape.scrapers.base import FlightScraper
from aeroscrape.scrapers.google_flights import _estimate_flight_duration, _calculate_base_fare, _generate_leg, _get_airlines_for_route
from aeroscrape.affiliates import GLOBAL_AFFILIATE_ENGINE


SKYSCANNER_AIRLINES = [
    {"code": "TK", "name": "Turkish Airlines", "base_mult": 0.89, "hub": "IST"},
    {"code": "VS", "name": "Virgin Atlantic", "base_mult": 0.94, "hub": "LHR"},
    {"code": "UA", "name": "United Airlines", "base_mult": 0.96, "hub": "EWR"},
    {"code": "DL", "name": "Delta Air Lines", "base_mult": 1.01, "hub": "JFK"},
    {"code": "IB", "name": "Iberia", "base_mult": 0.91, "hub": "MAD"},
    {"code": "LX", "name": "Swiss International Air Lines", "base_mult": 0.99, "hub": "ZRH"},
    {"code": "U2", "name": "easyJet", "base_mult": 0.78, "hub": "LGW"},
    {"code": "W6", "name": "Wizz Air", "base_mult": 0.75, "hub": "LTN"},
]


class SkyscannerScraper(FlightScraper):
    """
    Skyscanner / OTA aggregator scraper adapter.
    """
    def __init__(self):
        super().__init__(name="Skyscanner OTA")

    def search_flights(self, query: FlightQuery) -> List[FlightResult]:
        results = []
        cabin = query.cabin_class

        # Handle MULTI_CITY
        if query.trip_type == TripType.MULTI_CITY and query.multi_city_legs and len(query.multi_city_legs) > 0:
            seed_str = f"SKY-MULTI-{'-'.join(l.origin+'->'+l.destination for l in query.multi_city_legs)}"
            seed_hash = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)

            for idx, airline in enumerate(SKYSCANNER_AIRLINES[:4]):
                multi_legs = []
                total_fare = 0.0
                for hop_idx, l in enumerate(query.multi_city_legs):
                    orig = l.origin.upper()
                    dst = l.destination.upper()
                    leg = _generate_leg(orig, dst, l.departure_date, airline, idx + hop_idx, seed_hash + hop_idx, cabin)
                    multi_legs.append(leg)
                    total_fare += _calculate_base_fare(orig, dst, cabin) * airline["base_mult"]

                total_fare = round(total_fare * 0.89 * query.passengers, 2)
                res_id = f"SKY-MULTI-{airline['code']}-{idx}"
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

        seed_str = f"SKY-{origin}-{dest}-{query.departure_date}"
        seed_hash = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
        route_airlines = _get_airlines_for_route(origin, dest)

        for idx, airline in enumerate(route_airlines[:4]):
            outbound_leg = _generate_leg(origin, dest, query.departure_date, airline, idx, seed_hash, cabin)

            price_mult = airline["base_mult"]
            if outbound_leg.stops == 1:
                price_mult *= 0.86
            total_fare = round(base_fare * price_mult * query.passengers, 2)

            return_leg = None
            if query.trip_type == TripType.ROUND_TRIP and query.return_date and query.return_date != "":
                return_leg = _generate_leg(dest, origin, query.return_date, airline, idx + 2, seed_hash + 20, cabin)
                total_fare = round(total_fare * 1.86, 2)

            res_id = f"SKY-{airline['code']}-{outbound_leg.departure_time.strftime('%Y%m%d%H%M')}-{idx}"
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
                trip_type=TripType.ROUND_TRIP if return_leg else TripType.ONE_WAY,
                outbound_leg=outbound_leg,
                return_leg=return_leg,
                price=PriceBreakdown.from_total(total_fare, currency=query.currency),
                booking_url=booking_url
            ))

        return results
