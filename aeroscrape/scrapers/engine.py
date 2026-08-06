"""
Multi-Scraper Meta-Engine for AeroScrape.
Queries multiple flight sources, supports Metropolitan City Area Codes (e.g. NYC -> JFK/EWR/LGA),
deduplicates itineraries, evaluates Shabbos and Kosher meal compliance,
computes Best Value scores, and applies custom filters.
"""
import time
from typing import List, Tuple, Dict, Any, Optional

from aeroscrape.models import (
    FlightQuery,
    FlightResult,
    ScraperStats,
    ShabbosComplianceLevel,
)
from aeroscrape.airports import expand_city_to_airports
from aeroscrape.scrapers.base import FlightScraper
from aeroscrape.scrapers.live_google_flights import LiveGoogleFlightsScraper
from aeroscrape.scrapers.google_flights import GoogleFlightsScraper
from aeroscrape.scrapers.skyscanner import SkyscannerScraper
from aeroscrape.scrapers.airline_direct import DirectAirlineScraper
from aeroscrape.compliance.shabbos import evaluate_itinerary_shabbos_compliance
from aeroscrape.compliance.kosher import get_airline_kosher_info
from aeroscrape.compliance.delay_risk import evaluate_route_delay_risk
from aeroscrape.cache import GLOBAL_ROUTE_CACHE


class AeroScrapeEngine:
    """
    Unified Meta-Scraper engine combining Google Flights, Skyscanner OTA, and Direct Airline scrapers
    with Shabbos alerts, Kosher meal verification, and City Area expansion.
    """
    def __init__(self, scrapers: Optional[List[FlightScraper]] = None):
        if scrapers is None:
            self.scrapers = [
                LiveGoogleFlightsScraper(),
                GoogleFlightsScraper(),
                SkyscannerScraper(),
                DirectAirlineScraper(),
            ]
        else:
            self.scrapers = scrapers

    def search(self, query: FlightQuery) -> Tuple[List[FlightResult], ScraperStats]:
        # Check TTL Route Cache first
        cached = GLOBAL_ROUTE_CACHE.get(
            origin=query.origin,
            destination=query.destination,
            date=query.departure_date,
            return_date=query.return_date,
            cabin=query.cabin_class.value,
            pax=query.passengers,
            trip_type=query.trip_type.value
        )
        if cached is not None:
            c_flights, c_stats = cached
            c_stats_copy = c_stats.model_copy(update={"cache_hit": True, "execution_time_ms": 0.85})
            return c_flights, c_stats_copy

        start_time = time.time()
        raw_results: List[FlightResult] = []
        scrapers_queried: List[str] = []

        # Evaluate Historical Route Delay Risk & adjust Halachic Buffer automatically
        delay_risk = evaluate_route_delay_risk(query.origin, query.destination, query.shabbos_buffer_hours)
        effective_buffer_hours = delay_risk.recommended_buffer_hours

        # 1. Expand City Area Codes (e.g. NYC -> JFK, EWR, LGA)
        origin_airports = expand_city_to_airports(query.origin)
        dest_airports = expand_city_to_airports(query.destination)

        for orig in origin_airports:
            for dest in dest_airports:
                sub_query = query.model_copy(update={"origin": orig, "destination": dest})
                for scraper in self.scrapers:
                    if scraper.name not in scrapers_queried:
                        scrapers_queried.append(scraper.name)
                    try:
                        res = scraper.search_flights(sub_query)
                        raw_results.extend(res)
                    except Exception as e:
                        print(f"[Warning] Scraper '{scraper.name}' failed for {orig}-{dest}: {e}")

        # 2. Deduplicate similar flights (same airline + origin + dest + approx departure time)
        dedup_map: Dict[str, FlightResult] = {}
        for fl in raw_results:
            dep_hour_key = fl.outbound_leg.departure_time.strftime("%Y%m%d%H")
            key = f"{fl.outbound_leg.airline_code}-{fl.outbound_leg.origin}-{fl.outbound_leg.destination}-{dep_hour_key}"
            
            if key not in dedup_map:
                dedup_map[key] = fl
            else:
                if fl.price.total_price < dedup_map[key].price.total_price:
                    dedup_map[key] = fl

        unique_flights = list(dedup_map.values())

        # 3. Attach Shabbos Compliance and Kosher Meal Info
        for fl in unique_flights:
            fl.shabbos_status = evaluate_itinerary_shabbos_compliance(
                legs=fl.all_legs,
                buffer_hours=effective_buffer_hours
            )
            fl.kosher_info = get_airline_kosher_info(
                airline_code=fl.outbound_leg.airline_code,
                airline_name=fl.outbound_leg.airline_name
            )

        # 4. Apply Custom User Filters
        filtered_flights = []
        for fl in unique_flights:
            if query.filter_shabbos_violations and fl.shabbos_status:
                if fl.shabbos_status.level == ShabbosComplianceLevel.VIOLATION:
                    continue

            if query.require_ksml and fl.kosher_info:
                if not fl.kosher_info.ksml_offered:
                    continue

            if query.preferred_hechsher and query.preferred_hechsher.strip() != "":
                if query.preferred_hechsher.lower() not in fl.kosher_info.certification.lower():
                    continue

            if query.max_stops is not None:
                if fl.outbound_leg.stops > query.max_stops:
                    continue

            filtered_flights.append(fl)

        if not filtered_flights:
            exec_time = round((time.time() - start_time) * 1000.0, 2)
            return [], ScraperStats(
                total_found=0,
                cheapest_price=0.0,
                average_price=0.0,
                fastest_duration_minutes=0,
                shabbos_safe_count=0,
                kosher_available_count=0,
                scrapers_queried=scrapers_queried,
                execution_time_ms=exec_time
            )

        # 5. Compute Value Scores & Assign Tags
        min_price = min(f.price.total_price for f in filtered_flights)
        max_price = max(f.price.total_price for f in filtered_flights)
        min_dur = min(f.total_duration_minutes for f in filtered_flights)
        max_dur = max(f.total_duration_minutes for f in filtered_flights)

        for fl in filtered_flights:
            if max_price > min_price:
                price_score = 60.0 * (1.0 - (fl.price.total_price - min_price) / (max_price - min_price))
            else:
                price_score = 60.0

            if max_dur > min_dur:
                dur_score = 25.0 * (1.0 - (fl.total_duration_minutes - min_dur) / (max_dur - min_dur))
            else:
                dur_score = 25.0

            stops_score = 15.0 if fl.outbound_leg.stops == 0 else (5.0 if fl.outbound_leg.stops == 1 else 0.0)

            bonus = 0.0
            if fl.shabbos_status and fl.shabbos_status.level == ShabbosComplianceLevel.SAFE:
                bonus += 5.0
            if fl.kosher_info and fl.kosher_info.ksml_offered:
                bonus += 3.0
            if fl.kosher_info and fl.kosher_info.mehadrin_skml_offered:
                bonus += 2.0

            fl.value_score = round(min(100.0, price_score + dur_score + stops_score + bonus), 1)

            tags = []
            if fl.price.total_price == min_price:
                tags.append("Lowest Fare")
            if fl.outbound_leg.stops == 0:
                tags.append("Direct Flight")
            if fl.shabbos_status:
                if fl.shabbos_status.level == ShabbosComplianceLevel.SAFE:
                    tags.append("Shabbos Safe")
                elif fl.shabbos_status.level == ShabbosComplianceLevel.WARNING:
                    tags.append("Tight Shabbos Buffer")
                elif fl.shabbos_status.level == ShabbosComplianceLevel.VIOLATION:
                    tags.append("Shabbos Violation")
            if fl.kosher_info:
                if fl.kosher_info.mehadrin_skml_offered:
                    tags.append("Mehadrin KSML Available")
                elif fl.kosher_info.ksml_offered:
                    tags.append("KSML Available")
                else:
                    tags.append("No Kosher Meals")

            fl.tags = tags

        best_val_flight = max(filtered_flights, key=lambda f: f.value_score)
        if "Best Value" not in best_val_flight.tags:
            best_val_flight.tags.insert(0, "Best Value")

        filtered_flights.sort(key=lambda f: f.price.total_price)

        avg_price = round(sum(f.price.total_price for f in filtered_flights) / len(filtered_flights), 2)
        shabbos_safe_count = sum(1 for f in filtered_flights if f.shabbos_status and f.shabbos_status.level == ShabbosComplianceLevel.SAFE)
        kosher_count = sum(1 for f in filtered_flights if f.kosher_info and f.kosher_info.ksml_offered)
        exec_time = round((time.time() - start_time) * 1000.0, 2)

        stats = ScraperStats(
            total_found=len(filtered_flights),
            cheapest_price=min_price,
            average_price=avg_price,
            fastest_duration_minutes=min_dur,
            shabbos_safe_count=shabbos_safe_count,
            kosher_available_count=kosher_count,
            scrapers_queried=scrapers_queried,
            execution_time_ms=exec_time,
            cache_hit=False,
            delay_risk_level=delay_risk.risk_level,
            delay_risk_summary=f"Historical delay rate {delay_risk.historical_delay_rate_pct}%. Recommended safety buffer: {delay_risk.recommended_buffer_hours}h ({delay_risk.reason})"
        )

        GLOBAL_ROUTE_CACHE.set(
            origin=query.origin,
            destination=query.destination,
            date=query.departure_date,
            return_date=query.return_date,
            cabin=query.cabin_class.value,
            pax=query.passengers,
            trip_type=query.trip_type.value,
            data=(filtered_flights, stats)
        )

        return filtered_flights, stats
