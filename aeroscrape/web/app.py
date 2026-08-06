"""
FastAPI Backend for AeroScrape Flight Engine.
Provides REST API endpoints for flight searches, airport database, zmanim calculations, and kosher airline guides.
"""
import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from aeroscrape.models import FlightQuery, CabinClass
from aeroscrape.scrapers.engine import AeroScrapeEngine
from aeroscrape.analytics.price_analyzer import analyze_price_trend
from aeroscrape.airports import list_all_airports, get_airport, search_airports
from aeroscrape.compliance.shabbos import get_shabbos_zmanim
from aeroscrape.compliance.kosher import list_all_kosher_airlines
from aeroscrape.compliance.delay_risk import evaluate_route_delay_risk
from aeroscrape.compliance.feedback import GLOBAL_KASHRUT_FEEDBACK_DB, KosherMealReport
from aeroscrape.marketing.alerts import GLOBAL_FARE_ALERT_ENGINE
from aeroscrape.marketing.share import generate_share_summary
from aeroscrape.analytics.calendar import generate_month_calendar
from aeroscrape.cache import GLOBAL_ROUTE_CACHE
from aeroscrape.affiliates import GLOBAL_AFFILIATE_ENGINE


app = FastAPI(
    title="AeroScrape Flight Price Engine API",
    version="1.0.0",
    description="Professional Flight Scraper with Shabbos Alert System & Kosher Meal (KSML) Kashrut Verification"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def normalize_vercel_path(request, call_next):
    path = request.scope.get("path", "")
    for prefix in ["/api/index.py", "/api/index", "/index.py", "/index"]:
        if path.startswith(prefix):
            path = path[len(prefix):]
            if not path.startswith("/"):
                path = "/" + path
            request.scope["path"] = path
            break
    return await call_next(request)


@app.get("/api/airports")
@app.get("/airports", include_in_schema=False)
def get_airports():
    """Returns list of major international airports and Jewish travel hubs."""
    return list_all_airports()


@app.get("/api/airports/autocomplete")
@app.get("/airports/autocomplete", include_in_schema=False)
def get_airport_autocomplete(q: str = Query("", description="City name, airport code, or country")):
    """
    Autocomplete search for airports and metropolitan city areas (e.g. NYC, LON, PAR).
    Returns structured suggestions grouped by City (All Airports) first, then specific airports.
    """
    if not q or q.strip() == "":
        return search_airports("")
    return search_airports(q)


@app.get("/api/kosher-airlines")
@app.get("/kosher-airlines", include_in_schema=False)
def get_kosher_airlines():
    """Returns the complete Kosher Meal (KSML / SKML) database for all airlines."""
    return list_all_kosher_airlines()


@app.get("/api/zmanim")
@app.get("/zmanim", include_in_schema=False)
def get_zmanim(airport: str = Query(..., description="3-letter IATA airport code"), date: str = Query(..., description="YYYY-MM-DD")):
    """Calculates Sunset, Candle Lighting, and Havdalah times for an airport."""
    try:
        dt = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        dt = datetime.now().date()

    sunset, cl, hav = get_shabbos_zmanim(airport, dt)
    info = get_airport(airport)

    return {
        "airport": info.iata,
        "city": info.city,
        "country": info.country,
        "timezone": info.timezone,
        "date": dt.strftime("%Y-%m-%d"),
        "day_of_week": dt.strftime("%A"),
        "sunset_utc": sunset.isoformat(),
        "candle_lighting_utc": cl.isoformat(),
        "havdalah_utc": hav.isoformat(),
        "candle_lighting_time": cl.strftime("%H:%M UTC"),
        "havdalah_time": hav.strftime("%H:%M UTC"),
        "offset_minutes": info.candle_lighting_offset_minutes
    }


@app.get("/api/search")
@app.get("/search", include_in_schema=False)
def search_flights(
    origin: str = Query("JFK"),
    destination: str = Query("TLV"),
    departure_date: str = Query("2026-08-14"),
    return_date: Optional[str] = Query(None),
    passengers: int = Query(1),
    cabin_class: str = Query("economy"),
    shabbos_buffer_hours: float = Query(3.0),
    filter_shabbos_violations: bool = Query(True),
    require_ksml: bool = Query(False),
    max_stops: Optional[int] = Query(None)
):
    """
    Search flights across Google Flights, Skyscanner OTA, and Direct Airlines.
    Evaluates Shabbos alerts and Kosher meal kashrut.
    """
    try:
        cabin = CabinClass(cabin_class.lower())
    except ValueError:
        cabin = CabinClass.ECONOMY

    query = FlightQuery(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        passengers=passengers,
        cabin_class=cabin,
        shabbos_buffer_hours=shabbos_buffer_hours,
        filter_shabbos_violations=filter_shabbos_violations,
        require_ksml=require_ksml,
        max_stops=max_stops
    )

    engine = AeroScrapeEngine()
    flights, stats = engine.search(query)
    trend = analyze_price_trend(query, current_cheapest=stats.cheapest_price if flights else None, engine=engine)

    return {
        "query": query.model_dump(),
        "stats": stats.model_dump(),
        "trend": trend.model_dump(),
        "flights": [fl.model_dump() for fl in flights]
    }


@app.get("/api/delay-risk")
@app.get("/delay-risk", include_in_schema=False)
def get_delay_risk(origin: str = Query("JFK"), destination: str = Query("TLV"), base_buffer_hours: float = Query(3.0)):
    """Returns historical route delay risk and automatically adjusted Halachic safety buffer."""
    assessment = evaluate_route_delay_risk(origin, destination, base_buffer_hours)
    return assessment.model_dump()


@app.get("/api/calendar")
@app.get("/calendar", include_in_schema=False)
def get_month_calendar(
    origin: str = Query("JFK"),
    destination: str = Query("TLV"),
    year_month: str = Query("2026-08"),
    cabin_class: str = Query("economy"),
    passengers: int = Query(1)
):
    """Returns a 30-day Halachic fare calendar showing daily lowest prices and Shabbat safety indicators."""
    cal = generate_month_calendar(origin, destination, year_month, cabin_class, passengers)
    return cal.model_dump()


@app.get("/api/share")
@app.get("/share", include_in_schema=False)
def get_share_links(
    origin: str = Query("JFK"),
    destination: str = Query("TLV"),
    date: str = Query("2026-08-14"),
    airline: str = Query("IB"),
    flight_num: str = Query("IB440"),
    price: float = Query(533.81)
):
    """Returns WhatsApp-ready and printable text summaries for sharing flight deals."""
    from aeroscrape.models import FlightResult, FlightLeg, TripType, PriceBreakdown, CabinClass
    leg = FlightLeg(
        airline_code=airline.upper(),
        airline_name=f"Airline ({airline})",
        flight_number=flight_num,
        origin=origin.upper(),
        origin_city=f"City ({origin})",
        destination=destination.upper(),
        destination_city=f"City ({destination})",
        departure_time=datetime.strptime(f"{date} 20:15", "%Y-%m-%d %H:%M"),
        arrival_time=datetime.strptime(f"{date} 10:20", "%Y-%m-%d %H:%M"),
        duration_minutes=830,
        stops=1,
        stop_airports=["MAD"],
        aircraft="Boeing 787-9",
        cabin_class=CabinClass.ECONOMY
    )
    res = FlightResult(
        id="SHARE-DEMO-1",
        scraper_source="AeroScrape",
        trip_type=TripType.ONE_WAY,
        outbound_leg=leg,
        price=PriceBreakdown.from_total(price, currency="USD"),
        booking_url=f"https://tp.media/r?marker=760438.aeroscrape_web&p=4114&u=https%3A%2F%2Fwww.aviasales.com%2Fsearch%2F1408{origin}{destination}1"
    )
    return generate_share_summary(res)


@app.get("/api/kosher-reports")
@app.get("/kosher-reports", include_in_schema=False)
def get_kosher_reports(airline: Optional[str] = Query(None)):
    """Returns community-submitted Kosher meal (KSML) audit reports and satisfaction scores."""
    if airline and airline.strip() != "":
        return GLOBAL_KASHRUT_FEEDBACK_DB.get_airline_stats(airline).model_dump()
    reports = GLOBAL_KASHRUT_FEEDBACK_DB.get_reports()
    return {"total_reports": len(reports), "reports": [r.model_dump() for r in reports]}


@app.post("/api/kosher-report")
@app.post("/kosher-report", include_in_schema=False)
def submit_kosher_report(report: KosherMealReport):
    """Submits a new community Kosher meal experience audit report."""
    rep_id = GLOBAL_KASHRUT_FEEDBACK_DB.add_report(report)
    return {"status": "success", "id": rep_id, "message": "Report submitted and community stats updated!"}


@app.post("/api/alerts/subscribe")
@app.post("/alerts/subscribe", include_in_schema=False)
def subscribe_to_alerts(
    email: str = Query(...),
    origin: str = Query("JFK"),
    destination: str = Query("TLV"),
    holiday_period: str = Query("Passover 2027"),
    target_price: Optional[float] = Query(None)
):
    """Subscribes a traveler email to automated Shabbat-safe & Kosher fare drop alerts."""
    sub = GLOBAL_FARE_ALERT_ENGINE.subscribe(email, origin, destination, holiday_period, target_price)
    return {"status": "success", "subscription": sub.model_dump(), "message": f"Successfully subscribed {email} to alerts for {holiday_period}!"}


@app.get("/api/alerts/subscribers")
@app.get("/alerts/subscribers", include_in_schema=False)
def list_subscribers():
    """Returns active fare alert subscribers (Admin monitoring)."""
    subs = GLOBAL_FARE_ALERT_ENGINE.get_subscribers()
    return {"total_subscribers": len(subs), "subscribers": [s.model_dump() for s in subs]}


@app.get("/api/cache/stats")
@app.get("/cache/stats", include_in_schema=False)
def get_cache_stats():
    """Returns live high-performance route cache hit/miss statistics."""
    return GLOBAL_ROUTE_CACHE.get_stats()


@app.get("/api/affiliate/status")
@app.get("/affiliate/status", include_in_schema=False)
def get_affiliate_status():
    """Returns current active affiliate CPA tracking network and Marker ID."""
    return GLOBAL_AFFILIATE_ENGINE.get_config().model_dump()


@app.post("/api/affiliate/config")
@app.post("/affiliate/config", include_in_schema=False)
def update_affiliate_config(marker_id: str = Query(...), network: str = Query("travelpayouts")):
    """Updates the affiliate CPA tracking Marker ID and network."""
    GLOBAL_AFFILIATE_ENGINE.set_marker(marker_id, network)
    return {"status": "success", "config": GLOBAL_AFFILIATE_ENGINE.get_config().model_dump(), "message": f"Updated affiliate tracking to marker '{marker_id}' on network '{network}'!"}


# Static web frontend serving
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_index():
    """Serves the interactive HTML dashboard on Vercel and local environments."""
    candidates = [
        os.path.join(STATIC_DIR, "index.html"),
        os.path.join(os.getcwd(), "aeroscrape", "web", "static", "index.html"),
        os.path.join(os.getcwd(), "public", "index.html"),
        os.path.join(os.getcwd(), "sample_dashboard.html")
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return HTMLResponse(content=f.read())
            except Exception:
                return FileResponse(path)
    return {"message": "AeroScrape API is active on Vercel! Try /api/search or /api/affiliate/status"}
