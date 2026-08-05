"""
Automated unit tests for AeroScrape Flight Engine, Shabbos alerts, Kosher kashrut directory, and multi-scraper engine.
"""
from datetime import datetime, date
import pytest

from aeroscrape.models import (
    FlightQuery,
    FlightLeg,
    CabinClass,
    ShabbosComplianceLevel,
)
from aeroscrape.compliance.shabbos import (
    evaluate_flight_shabbos_compliance,
    get_shabbos_zmanim,
)
from aeroscrape.compliance.kosher import get_airline_kosher_info, list_all_kosher_airlines
from aeroscrape.scrapers.engine import AeroScrapeEngine
from aeroscrape.analytics.price_analyzer import analyze_price_trend


def test_shabbos_zmanim_calculation():
    """Verify sunset, candle lighting, and havdalah calculation for TLV and JFK."""
    sunset, cl, hav = get_shabbos_zmanim("TLV", date(2026, 8, 14))
    assert sunset is not None
    assert cl < sunset
    assert hav > sunset
    # Candle lighting is 20 minutes before sunset for TLV
    assert (sunset - cl).total_seconds() == 20 * 60
    # Havdalah is 50 minutes after sunset
    assert (hav - sunset).total_seconds() == 50 * 60


def test_shabbos_compliance_friday_arrival_violation():
    """Flight arriving Friday night after candle lighting must be flagged as a VIOLATION."""
    # Create a Friday flight arriving at 21:00 UTC (after sunset/candle lighting)
    dep = datetime(2026, 8, 14, 8, 0, 0)
    arr = datetime(2026, 8, 14, 21, 0, 0)
    leg = FlightLeg(
        airline_code="UA",
        airline_name="United Airlines",
        flight_number="UA84",
        origin="JFK",
        origin_city="New York",
        destination="TLV",
        destination_city="Tel Aviv",
        departure_time=dep,
        arrival_time=arr,
        duration_minutes=780
    )

    status = evaluate_flight_shabbos_compliance(leg, buffer_hours=3.0)
    assert status.level == ShabbosComplianceLevel.VIOLATION
    assert status.is_shabbos_flight is True
    assert "AFTER Candle Lighting" in status.details[0]


def test_shabbos_compliance_friday_arrival_safe():
    """Flight arriving Friday early morning comfortably before Shabbos must be flagged as SAFE."""
    dep = datetime(2026, 8, 14, 0, 15, 0)
    arr = datetime(2026, 8, 14, 11, 0, 0)
    leg = FlightLeg(
        airline_code="LY",
        airline_name="El Al Israel Airlines",
        flight_number="LY2",
        origin="JFK",
        origin_city="New York",
        destination="TLV",
        destination_city="Tel Aviv",
        departure_time=dep,
        arrival_time=arr,
        duration_minutes=645
    )

    status = evaluate_flight_shabbos_compliance(leg, buffer_hours=3.0)
    assert status.level == ShabbosComplianceLevel.SAFE


def test_kosher_airline_directory():
    """Verify kashrut supervision rules and lead times."""
    elal = get_airline_kosher_info("LY")
    assert elal.ksml_offered is True
    assert elal.mehadrin_skml_offered is True
    assert elal.advance_notice_hours == 0
    assert "Badatz" in elal.certification

    ba = get_airline_kosher_info("BA")
    assert ba.ksml_offered is True
    assert "Hermolis" in ba.certification

    ryanair = get_airline_kosher_info("FR")
    assert ryanair.ksml_offered is False
    assert ryanair.rating == "C"

    all_airlines = list_all_kosher_airlines()
    assert len(all_airlines) >= 15


def test_aeroscrape_engine_search_and_filter():
    """Verify multi-scraper engine deduplication, scoring, and Shabbos violation filtering."""
    query = FlightQuery(
        origin="JFK",
        destination="TLV",
        departure_date="2026-08-14",
        passengers=1,
        cabin_class=CabinClass.ECONOMY,
        shabbos_buffer_hours=3.0,
        filter_shabbos_violations=True,
        require_ksml=True
    )

    engine = AeroScrapeEngine()
    flights, stats = engine.search(query)

    assert stats.total_found > 0
    assert stats.cheapest_price > 0
    assert len(stats.scrapers_queried) == 3  # Google Flights, Skyscanner OTA, Direct Airline

    for fl in flights:
        # All returned flights must not violate Shabbos when filter_shabbos_violations is True
        assert fl.shabbos_status.level != ShabbosComplianceLevel.VIOLATION
        # All returned flights must have KSML offered
        assert fl.kosher_info.ksml_offered is True
        # Must have a valid value score between 0 and 100
        assert 0.0 <= fl.value_score <= 100.0


def test_price_trend_analysis():
    """Verify 7-day flexible date grid and savings calculations."""
    query = FlightQuery(
        origin="JFK",
        destination="TLV",
        departure_date="2026-08-14"
    )

    trend = analyze_price_trend(query)
    assert len(trend.date_grid) == 7
    assert trend.benchmark_price > 0
    assert trend.price_verdict in ["Great Deal!", "Fair Price", "High Fare"]


def test_city_area_expansion_and_autocomplete():
    """Verify that city area codes expand into member airports and autocomplete search works."""
    from aeroscrape.airports import expand_city_to_airports, search_airports

    # 1. Check NYC expansion
    nyc_airports = expand_city_to_airports("NYC")
    assert "JFK" in nyc_airports
    assert "EWR" in nyc_airports
    assert "LGA" in nyc_airports

    # 2. Check London expansion
    lon_airports = expand_city_to_airports("LON")
    assert "LHR" in lon_airports
    assert "LGW" in lon_airports

    # 3. Check Autocomplete search
    res = search_airports("new")
    city_matches = [r for r in res if r["type"] == "city"]
    airport_matches = [r for r in res if r["type"] == "airport"]

    assert len(city_matches) >= 1  # NYC
    assert len(airport_matches) >= 2  # JFK, EWR


def test_trip_type_picker_and_multi_city():
    """Verify One-Way, Round-Trip, and Multi-City trip type queries across all scrapers."""
    from aeroscrape.models import FlightQuery, MultiCityLeg, TripType
    from aeroscrape.scrapers.engine import AeroScrapeEngine

    engine = AeroScrapeEngine()

    # 1. One-Way
    q_ow = FlightQuery(trip_type=TripType.ONE_WAY, origin="JFK", destination="TLV", departure_date="2026-08-14")
    ow_flights, ow_stats = engine.search(q_ow)
    assert ow_stats.total_found > 0
    assert ow_flights[0].return_leg is None

    # 2. Round-Trip
    q_rt = FlightQuery(trip_type=TripType.ROUND_TRIP, origin="JFK", destination="TLV", departure_date="2026-08-14", return_date="2026-08-23")
    rt_flights, rt_stats = engine.search(q_rt)
    assert rt_stats.total_found > 0
    assert rt_flights[0].return_leg is not None

    # 3. Multi-City
    q_mc = FlightQuery(
        trip_type=TripType.MULTI_CITY,
        origin="JFK",
        destination="TLV",
        departure_date="2026-08-14",
        multi_city_legs=[
            MultiCityLeg(origin="JFK", destination="LHR", departure_date="2026-08-14"),
            MultiCityLeg(origin="LHR", destination="CDG", departure_date="2026-08-18"),
            MultiCityLeg(origin="CDG", destination="TLV", departure_date="2026-08-22"),
        ],
        filter_shabbos_violations=False
    )
    mc_flights, mc_stats = engine.search(q_mc)
    assert mc_stats.total_found > 0
    assert len(mc_flights[0].multi_legs) == 3


def test_automated_production_engines():
    """Verify TTL Cache, Delay Risk Buffer Adjustment, Crowdsourced Kashrut Reports, and Alert Subscriptions."""
    from aeroscrape.compliance.delay_risk import evaluate_route_delay_risk
    from aeroscrape.compliance.feedback import GLOBAL_KASHRUT_FEEDBACK_DB, KosherMealReport
    from aeroscrape.marketing.alerts import GLOBAL_FARE_ALERT_ENGINE
    from aeroscrape.cache import GLOBAL_ROUTE_CACHE

    # 1. Test Delay Risk
    risk = evaluate_route_delay_risk("JFK", "TLV", base_buffer_hours=3.0)
    assert risk.risk_level == "HIGH"
    assert risk.recommended_buffer_hours >= 4.0

    # 2. Test Crowdsourced Kosher Meal Audit Report
    report = KosherMealReport(
        id="TEST-REP-1",
        airline_code="LY",
        airline_name="El Al",
        flight_number="LY4",
        travel_date="2026-08-01",
        ksml_received=True,
        rating=5,
        hechsher_observed="Badatz",
        comment="Perfect meal"
    )
    GLOBAL_KASHRUT_FEEDBACK_DB.add_report(report)
    stats = GLOBAL_KASHRUT_FEEDBACK_DB.get_airline_stats("LY")
    assert stats.total_reports >= 2
    assert stats.success_rate_pct > 90.0

    # 3. Test Fare Drop Alert Lead Capture
    sub = GLOBAL_FARE_ALERT_ENGINE.subscribe("user@test.com", "JFK", "TLV", "Passover 2027", target_price=700.0)
    alert_check = GLOBAL_FARE_ALERT_ENGINE.check_matching_alerts("JFK", "TLV", 650.0)
    assert alert_check["triggered_alerts_count"] >= 1

    # 4. Test TTL Cache Stats
    cache_stats = GLOBAL_ROUTE_CACHE.get_stats()
    assert "hit_rate_pct" in cache_stats



