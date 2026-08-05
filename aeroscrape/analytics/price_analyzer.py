"""
Price Analysis & Flexible Date Finder for AeroScrape.
Analyzes fare trends, identifies cheapest travel dates across a 7-day window,
and computes historical price benchmarks.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel

from aeroscrape.models import FlightQuery, FlightResult, CabinClass
from aeroscrape.scrapers.engine import AeroScrapeEngine
from aeroscrape.scrapers.google_flights import _calculate_base_fare


class DatePricePoint(BaseModel):
    date: str                  # YYYY-MM-DD
    day_of_week: str           # e.g. "Monday"
    cheapest_price: float
    cheapest_airline: str
    is_target_date: bool
    shabbos_safe: bool
    status: str                # "Cheapest", "Good Deal", "Standard", "High"


class PriceTrendAnalysis(BaseModel):
    origin: str
    destination: str
    target_date: str
    target_price: float
    benchmark_price: float
    price_verdict: str         # "Great Deal!", "Fair Price", "High Fare"
    verdict_summary: str
    date_grid: List[DatePricePoint]
    recommended_date: str
    potential_savings: float


def analyze_price_trend(
    query: FlightQuery,
    current_cheapest: Optional[float] = None,
    engine: Optional[AeroScrapeEngine] = None
) -> PriceTrendAnalysis:
    """
    Analyzes whether the current fare is a good deal compared to benchmarks,
    and scans a 7-day window (±3 days) to find the cheapest travel date.
    """
    if engine is None:
        engine = AeroScrapeEngine()

    origin = query.origin.upper()
    dest = query.destination.upper()
    target_dt = datetime.strptime(query.departure_date, "%Y-%m-%d").date()

    benchmark_fare = _calculate_base_fare(origin, dest, query.cabin_class) * query.passengers

    date_grid: List[DatePricePoint] = []
    cheapest_in_grid_price = float("inf")
    cheapest_in_grid_date = query.departure_date

    # Scan from -3 days to +3 days around target departure_date
    for offset in range(-3, 4):
        check_dt = target_dt + timedelta(days=offset)
        check_str = check_dt.strftime("%Y-%m-%d")
        
        # Build lightweight query for date check
        sub_query = FlightQuery(
            origin=origin,
            destination=dest,
            departure_date=check_str,
            passengers=query.passengers,
            cabin_class=query.cabin_class,
            currency=query.currency,
            shabbos_buffer_hours=query.shabbos_buffer_hours,
            filter_shabbos_violations=False
        )

        flights, stats = engine.search(sub_query)
        if not flights:
            continue

        cheapest_fl = flights[0]
        price = cheapest_fl.price.total_price

        # Check if cheapest flight is Shabbos safe
        is_safe = (
            cheapest_fl.shabbos_status is None or 
            cheapest_fl.shabbos_status.level == "SAFE"
        )

        # Classify deal status relative to benchmark
        if price < benchmark_fare * 0.90:
            status = "Great Deal"
        elif price < benchmark_fare * 1.05:
            status = "Good Deal"
        elif price < benchmark_fare * 1.20:
            status = "Standard"
        else:
            status = "High"

        pt = DatePricePoint(
            date=check_str,
            day_of_week=check_dt.strftime("%A"),
            cheapest_price=price,
            cheapest_airline=cheapest_fl.outbound_leg.airline_name,
            is_target_date=(offset == 0),
            shabbos_safe=is_safe,
            status=status
        )

        # Prefer Shabbos safe dates when picking the recommended cheapest date
        if is_safe and price < cheapest_in_grid_price:
            cheapest_in_grid_price = price
            cheapest_in_grid_date = check_str

        date_grid.append(pt)

    # Use current_cheapest if provided, otherwise target date's cheapest from grid
    target_pt = next((p for p in date_grid if p.is_target_date), None)
    target_price = current_cheapest if current_cheapest else (target_pt.cheapest_price if target_pt else benchmark_fare)

    # Determine verdict
    ratio = target_price / benchmark_fare
    if ratio < 0.90:
        verdict = "Great Deal!"
        summary = f"Fares on {query.departure_date} are ~{round((1.0 - ratio)*100)}% below average for {origin}-{dest}."
    elif ratio <= 1.06:
        verdict = "Fair Price"
        summary = f"Fares on {query.departure_date} are typical for this route and cabin class."
    else:
        verdict = "High Fare"
        summary = f"Fares on {query.departure_date} are ~{round((ratio - 1.0)*100)}% higher than normal. Consider shifting dates."

    potential_savings = max(0.0, round(target_price - cheapest_in_grid_price, 2))

    return PriceTrendAnalysis(
        origin=origin,
        destination=dest,
        target_date=query.departure_date,
        target_price=target_price,
        benchmark_price=round(benchmark_fare, 2),
        price_verdict=verdict,
        verdict_summary=summary,
        date_grid=date_grid,
        recommended_date=cheapest_in_grid_date,
        potential_savings=potential_savings
    )
