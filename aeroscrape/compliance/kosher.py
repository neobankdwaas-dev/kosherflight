"""
Kosher Meal (KSML / SKML) & Kashrut Verification Engine for AeroScrape.
Includes an authoritative database of airline kashrut standards, supervision agencies,
lead times, and recommendations based on 2026 airline policies.
"""
from typing import Dict, Optional, List
from aeroscrape.models import KosherMealInfo


AIRLINE_KOSHER_DATABASE: Dict[str, KosherMealInfo] = {
    # Israel Flag Carrier - Gold Standard
    "LY": KosherMealInfo(
        airline_code="LY",
        airline_name="El Al Israel Airlines",
        ksml_offered=True,
        mehadrin_skml_offered=True,
        advance_notice_hours=0,
        certification="Badatz Edah HaChareidit / Regal Kashrut",
        notes="All standard meals are Kosher. Mehadrin Badatz (SKML) can be requested at booking with no fee.",
        is_recommended=True,
        rating="A+"
    ),
    # US Major Carriers
    "UA": KosherMealInfo(
        airline_code="UA",
        airline_name="United Airlines",
        ksml_offered=True,
        mehadrin_skml_offered=False,
        advance_notice_hours=24,
        certification="MK Kosher (Montreal) / OU",
        notes="Available on international long-haul and US domestic flights >2,000 miles in Business/First Class. Request 24h before departure.",
        is_recommended=True,
        rating="A"
    ),
    "DL": KosherMealInfo(
        airline_code="DL",
        airline_name="Delta Air Lines",
        ksml_offered=True,
        mehadrin_skml_offered=False,
        advance_notice_hours=24,
        certification="OU (Orthodox Union) / Borenstein",
        notes="Available on international long-haul and select domestic premium routes. Request 24-48h in advance.",
        is_recommended=True,
        rating="A"
    ),
    "AA": KosherMealInfo(
        airline_code="AA",
        airline_name="American Airlines",
        ksml_offered=True,
        mehadrin_skml_offered=False,
        advance_notice_hours=24,
        certification="cRc (Chicago Rabbinical Council) / Fresko",
        notes="Available on international long-haul, select Brazil routes, and US domestic First Class where meals are served. Request 24h prior.",
        is_recommended=True,
        rating="A"
    ),
    # UK & European Flag Carriers
    "BA": KosherMealInfo(
        airline_code="BA",
        airline_name="British Airways",
        ksml_offered=True,
        mehadrin_skml_offered=True,
        advance_notice_hours=24,
        certification="Hermolis (Kedassia / London Badatz Standard)",
        notes="Hermolis meals are widely considered among the highest quality and strictest hechsherim in airline catering. Highly recommended.",
        is_recommended=True,
        rating="A+"
    ),
    "LH": KosherMealInfo(
        airline_code="LH",
        airline_name="Lufthansa",
        ksml_offered=True,
        mehadrin_skml_offered=False,
        advance_notice_hours=48,
        certification="OU / Sohar / Regal Kashrut",
        notes="Available on all long-haul flights from Frankfurt and Munich. Request at least 48h in advance.",
        is_recommended=True,
        rating="A"
    ),
    "AF": KosherMealInfo(
        airline_code="AF",
        airline_name="Air France",
        ksml_offered=True,
        mehadrin_skml_offered=False,
        advance_notice_hours=48,
        certification="Paris Orthodox Chief Rabbinate / Streeat Kosher",
        notes="Available on international long-haul flights departing Paris CDG/ORY. 48 hours notice required.",
        is_recommended=True,
        rating="A"
    ),
    "LX": KosherMealInfo(
        airline_code="LX",
        airline_name="Swiss International Air Lines",
        ksml_offered=True,
        mehadrin_skml_offered=False,
        advance_notice_hours=48,
        certification="OU / Rabbinat Zürich",
        notes="Excellent kosher catering out of Zurich. Must be booked 48 hours before departure.",
        is_recommended=True,
        rating="A"
    ),
    "KL": KosherMealInfo(
        airline_code="KL",
        airline_name="KLM Royal Dutch Airlines",
        ksml_offered=True,
        mehadrin_skml_offered=False,
        advance_notice_hours=48,
        certification="OU / Dutch Chief Rabbinate",
        notes="Available on all intercontinental KLM flights. 48h advance booking required.",
        is_recommended=True,
        rating="A"
    ),
    "AC": KosherMealInfo(
        airline_code="AC",
        airline_name="Air Canada",
        ksml_offered=True,
        mehadrin_skml_offered=False,
        advance_notice_hours=24,
        certification="MK Kosher (Montreal Vaad HaIr)",
        notes="Available on international long-haul flights and North American flights over 3 hours in Business Class.",
        is_recommended=True,
        rating="A"
    ),
    "VS": KosherMealInfo(
        airline_code="VS",
        airline_name="Virgin Atlantic",
        ksml_offered=True,
        mehadrin_skml_offered=True,
        advance_notice_hours=24,
        certification="Hermolis (Kedassia / London)",
        notes="Features Hermolis kosher meals out of London Heathrow and Gatwick. Excellent quality.",
        is_recommended=True,
        rating="A+"
    ),
    "IB": KosherMealInfo(
        airline_code="IB",
        airline_name="Iberia",
        ksml_offered=True,
        mehadrin_skml_offered=False,
        advance_notice_hours=48,
        certification="Madrid Rabbinate / OU",
        notes="Available on long-haul flights. Request 48h prior.",
        is_recommended=True,
        rating="B"
    ),
    "TK": KosherMealInfo(
        airline_code="TK",
        airline_name="Turkish Airlines",
        ksml_offered=True,
        mehadrin_skml_offered=False,
        advance_notice_hours=48,
        certification="OU (from Istanbul/US)",
        notes="KSML offered on select international flights. Confirm with customer service after booking.",
        is_recommended=True,
        rating="B"
    ),
    # Airlines WITHOUT KSML or Low-Cost Carriers
    "FR": KosherMealInfo(
        airline_code="FR",
        airline_name="Ryanair",
        ksml_offered=False,
        advance_notice_hours=0,
        certification="None",
        notes="Low-cost carrier: no special dietary meals or kosher food service provided on board.",
        is_recommended=False,
        rating="C"
    ),
    "U2": KosherMealInfo(
        airline_code="U2",
        airline_name="easyJet",
        ksml_offered=False,
        advance_notice_hours=0,
        certification="None",
        notes="Low-cost carrier: no kosher meal pre-order available. Remember to bring Kosher food with you!",
        is_recommended=False,
        rating="C"
    ),
    "W6": KosherMealInfo(
        airline_code="W6",
        airline_name="Wizz Air",
        ksml_offered=False,
        advance_notice_hours=0,
        certification="None",
        notes="Low-cost carrier: no kosher food service. Remember to bring Kosher food with you!",
        is_recommended=False,
        rating="C"
    ),
    "NK": KosherMealInfo(
        airline_code="NK",
        airline_name="Spirit Airlines",
        ksml_offered=False,
        advance_notice_hours=0,
        certification="None",
        notes="No complimentary meal service or KSML options available.",
        is_recommended=False,
        rating="C"
    ),
    "F9": KosherMealInfo(
        airline_code="F9",
        airline_name="Frontier Airlines",
        ksml_offered=False,
        advance_notice_hours=0,
        certification="None",
        notes="No special meal requests supported.",
        is_recommended=False,
        rating="C"
    ),
    "EK": KosherMealInfo(
        airline_code="EK",
        airline_name="Emirates",
        ksml_offered=False,
        advance_notice_hours=0,
        certification="Halal Standard Only",
        notes="Kosher meals (KSML) are no longer offered on Emirates routes. Only standard Halal catering is provided.",
        is_recommended=False,
        rating="C"
    ),
    "QR": KosherMealInfo(
        airline_code="QR",
        airline_name="Qatar Airways",
        ksml_offered=False,
        advance_notice_hours=0,
        certification="Halal Standard Only",
        notes="Does not offer KSML (Kosher meals) on its flights.",
        is_recommended=False,
        rating="C"
    ),
}


def get_airline_kosher_info(airline_code: str, airline_name: Optional[str] = None) -> KosherMealInfo:
    """
    Returns detailed KosherMealInfo for the given airline code.
    If unknown, returns a default info indicating general KSML rules.
    """
    code = airline_code.upper().strip()
    if code in AIRLINE_KOSHER_DATABASE:
        return AIRLINE_KOSHER_DATABASE[code]

    # Check by name substring
    if airline_name:
        for info in AIRLINE_KOSHER_DATABASE.values():
            if info.airline_name.lower() in airline_name.lower() or airline_name.lower() in info.airline_name.lower():
                return info

    # Default fallback for unlisted full-service international carriers
    return KosherMealInfo(
        airline_code=code,
        airline_name=airline_name or f"Airline ({code})",
        ksml_offered=True,
        mehadrin_skml_offered=False,
        advance_notice_hours=48,
        certification="Standard Rabbinical Supervision (Verify with Airline)",
        notes="Standard KSML available on most international long-haul flights with 48h notice.",
        is_recommended=True,
        rating="B"
    )


def list_all_kosher_airlines() -> List[KosherMealInfo]:
    """Returns all airlines in the Kosher database sorted by rating."""
    return sorted(AIRLINE_KOSHER_DATABASE.values(), key=lambda x: (x.rating, x.airline_name))
