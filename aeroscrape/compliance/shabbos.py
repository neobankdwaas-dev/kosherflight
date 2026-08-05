"""
Shabbos & Yom Tov Alert System for AeroScrape Flight Engine.
Calculates astronomical sunset, Candle Lighting, and Havdalah times for origin and destination airports,
and evaluates multi-leg flight itineraries against halachic travel safety buffers.
"""
import math
from datetime import datetime, date, timedelta, time
from typing import Optional, Tuple, Dict, Any, List

from aeroscrape.models import ShabbosStatus, ShabbosComplianceLevel, FlightLeg
from aeroscrape.airports import get_airport, AirportInfo


def _deg2rad(deg: float) -> float:
    return deg * math.pi / 180.0


def _rad2deg(rad: float) -> float:
    return rad * 180.0 / math.pi


def calculate_sunset_utc(dt: date, lat: float, lon: float) -> Optional[datetime]:
    """
    Calculate astronomical sunset time in UTC for a given date, latitude, and longitude
    using the NOAA solar calculation algorithms.
    """
    year = dt.year
    month = dt.month
    day = dt.day

    N1 = math.floor(275 * month / 9)
    N2 = math.floor((month + 9) / 12)
    N3 = (1 + math.floor((year - 4 * math.floor(year / 4) + 2) / 3))
    N = N1 - (N2 * N3) + day - 30

    lngHour = lon / 15.0
    t = N + ((18 - lngHour) / 24.0)

    M = (0.9856 * t) - 3.289

    L = M + (1.916 * math.sin(_deg2rad(M))) + (0.020 * math.sin(_deg2rad(2 * M))) + 282.634
    L = (L + 360) % 360

    RA = _rad2deg(math.atan(0.91764 * math.tan(_deg2rad(L))))
    RA = (RA + 360) % 360

    Lquadrant = (math.floor(L / 90)) * 90
    RAquadrant = (math.floor(RA / 90)) * 90
    RA = RA + (Lquadrant - RAquadrant)

    RA = RA / 15.0

    sinDec = 0.39782 * math.sin(_deg2rad(L))
    cosDec = math.cos(math.asin(sinDec))

    cosH = (math.cos(_deg2rad(90.833)) - (sinDec * math.sin(_deg2rad(lat)))) / (cosDec * math.cos(_deg2rad(lat)))

    if cosH > 1:
        return None
    if cosH < -1:
        return None

    H = _rad2deg(math.acos(cosH)) / 15.0

    T = H + RA - (0.06571 * t) - 6.622

    UT = (T - lngHour + 24) % 24

    hours = int(UT)
    minutes = int((UT - hours) * 60)
    seconds = int((((UT - hours) * 60) - minutes) * 60)

    return datetime(year, month, day, hours, minutes, seconds)


def get_shabbos_zmanim(airport_code: str, dt: date) -> Tuple[datetime, datetime, datetime]:
    """
    Returns (Sunset, Candle Lighting, Havdalah) for the airport on the given date.
    """
    airport = get_airport(airport_code)
    sunset = calculate_sunset_utc(dt, airport.lat, airport.lon)
    if not sunset:
        sunset = datetime(dt.year, dt.month, dt.day, 18, 0, 0)
    
    candle_lighting = sunset - timedelta(minutes=airport.candle_lighting_offset_minutes)
    havdalah = sunset + timedelta(minutes=50)
    return sunset, candle_lighting, havdalah


def evaluate_flight_shabbos_compliance(
    leg: FlightLeg,
    buffer_hours: float = 3.0
) -> ShabbosStatus:
    """
    Evaluates a single flight leg for Shabbos compliance.
    """
    details = []
    dep_time = leg.departure_time
    arr_time = leg.arrival_time

    origin_airport = get_airport(leg.origin)
    dest_airport = get_airport(leg.destination)

    dep_weekday = dep_time.weekday()
    arr_weekday = arr_time.weekday()

    buffer_mins = int(buffer_hours * 60)

    # 1. Check if flight departs on Friday and arrives after candle lighting
    if dep_weekday == 4:
        _, cl_dest, _ = get_shabbos_zmanim(leg.destination, arr_time.date())
        diff_mins = int((cl_dest - arr_time).total_seconds() / 60)
        
        cl_str = cl_dest.strftime("%H:%M")
        arr_str = arr_time.strftime("%H:%M")
        
        if diff_mins < 0:
            msg = f"SHABBOS VIOLATION: Flight arrives in {leg.destination_city} at {arr_str} Friday, which is AFTER Candle Lighting ({cl_str})."
            details.append(msg)
            return ShabbosStatus(
                level=ShabbosComplianceLevel.VIOLATION,
                is_shabbos_flight=True,
                dest_candle_lighting=cl_dest,
                buffer_minutes=diff_mins,
                summary="⚠️ Not Recommended for Shabbos (Arrives after Candle Lighting)",
                details=details
            )
        elif diff_mins < buffer_mins:
            msg = (
                f"TIGHT BUFFER WARNING: Flight arrives in {leg.destination_city} at {arr_str} Friday, "
                f"only {diff_mins // 60}h {diff_mins % 60}m before Candle Lighting ({cl_str})."
            )
            details.append(msg)
            return ShabbosStatus(
                level=ShabbosComplianceLevel.WARNING,
                is_shabbos_flight=True,
                dest_candle_lighting=cl_dest,
                buffer_minutes=diff_mins,
                summary=f"Tight Friday Arrival Buffer ({diff_mins // 60}h {diff_mins % 60}m)",
                details=details
            )
        else:
            msg = f"SAFE FRIDAY FLIGHT: Arrives in {leg.destination_city} at {arr_str}, {diff_mins // 60}h {diff_mins % 60}m before Candle Lighting ({cl_str})."
            details.append(msg)
            return ShabbosStatus(
                level=ShabbosComplianceLevel.SAFE,
                is_shabbos_flight=True,
                dest_candle_lighting=cl_dest,
                buffer_minutes=diff_mins,
                summary=f"Safe Friday Flight ({diff_mins // 60}h {diff_mins % 60}m buffer)",
                details=details
            )

    # 2. Check if flight departs on Saturday
    if dep_weekday == 5:
        _, _, hav_origin = get_shabbos_zmanim(leg.origin, dep_time.date())
        diff_mins = int((dep_time - hav_origin).total_seconds() / 60)
        
        hav_str = hav_origin.strftime("%H:%M")
        dep_str = dep_time.strftime("%H:%M")

        if diff_mins < 0:
            msg = f"SHABBOS VIOLATION: Flight departs {leg.origin_city} at {dep_str} Saturday, BEFORE Havdalah ({hav_str})."
            details.append(msg)
            return ShabbosStatus(
                level=ShabbosComplianceLevel.VIOLATION,
                is_shabbos_flight=True,
                origin_havdalah=hav_origin,
                buffer_minutes=diff_mins,
                summary="⚠️ Not Recommended for Shabbos (Departs before Havdalah)",
                details=details
            )
        elif diff_mins < 120:
            msg = f"WARNING (MOTZEI SHABBOS): Flight departs at {dep_str}, only {diff_mins // 60}h {diff_mins % 60}m after Havdalah ({hav_str})."
            details.append(msg)
            return ShabbosStatus(
                level=ShabbosComplianceLevel.WARNING,
                is_shabbos_flight=True,
                origin_havdalah=hav_origin,
                buffer_minutes=diff_mins,
                summary=f"Motzei Shabbos Tight Departure ({diff_mins // 60}h {diff_mins % 60}m after Havdalah)",
                details=details
            )
        else:
            msg = f"SAFE MOTZEI SHABBOS FLIGHT: Departs at {dep_str}, comfortably after Havdalah ({hav_str})."
            details.append(msg)
            return ShabbosStatus(
                level=ShabbosComplianceLevel.SAFE,
                is_shabbos_flight=True,
                origin_havdalah=hav_origin,
                buffer_minutes=diff_mins,
                summary="Safe Motzei Shabbos Flight",
                details=details
            )

    # 3. Overnight Friday->Saturday
    if dep_weekday == 4 and arr_weekday == 5:
        msg = "SHABBOS VIOLATION: Flight departs Friday and is airborne into Saturday Shabbos."
        details.append(msg)
        return ShabbosStatus(
            level=ShabbosComplianceLevel.VIOLATION,
            is_shabbos_flight=True,
            summary="⚠️ Not Recommended for Shabbos (Airborne during Shabbos)",
            details=details
        )

    return ShabbosStatus(
        level=ShabbosComplianceLevel.SAFE,
        is_shabbos_flight=False,
        summary="Weekday Flight (No Shabbos Conflict)",
        details=[f"Departs on {dep_time.strftime('%A')} and arrives on {arr_time.strftime('%A')} - fully compliant."]
    )


def evaluate_itinerary_shabbos_compliance(
    legs: List[FlightLeg],
    buffer_hours: float = 3.0
) -> ShabbosStatus:
    """
    Evaluates an entire multi-leg itinerary (One-Way, Round-Trip, or Multi-City)
    for Shabbos compliance across all legs.
    """
    if not legs:
        return ShabbosStatus(level=ShabbosComplianceLevel.SAFE, summary="No flight legs to evaluate")

    leg_statuses = [evaluate_flight_shabbos_compliance(l, buffer_hours) for l in legs]
    all_details = []
    for idx, (leg, st) in enumerate(zip(legs, leg_statuses), 1):
        prefix = f"Leg {idx} ({leg.origin}→{leg.destination}): " if len(legs) > 1 else ""
        for d in st.details:
            all_details.append(f"{prefix}{d}")

    # Check for any violations
    for idx, (leg, st) in enumerate(zip(legs, leg_statuses), 1):
        if st.level == ShabbosComplianceLevel.VIOLATION:
            prefix = f"Leg {idx}: " if len(legs) > 1 else ""
            return ShabbosStatus(
                level=ShabbosComplianceLevel.VIOLATION,
                is_shabbos_flight=True,
                dest_candle_lighting=st.dest_candle_lighting,
                origin_havdalah=st.origin_havdalah,
                buffer_minutes=st.buffer_minutes,
                summary=f"{prefix}{st.summary}",
                details=all_details
            )

    # Check for any warnings
    for idx, (leg, st) in enumerate(zip(legs, leg_statuses), 1):
        if st.level == ShabbosComplianceLevel.WARNING:
            prefix = f"Leg {idx}: " if len(legs) > 1 else ""
            return ShabbosStatus(
                level=ShabbosComplianceLevel.WARNING,
                is_shabbos_flight=True,
                dest_candle_lighting=st.dest_candle_lighting,
                origin_havdalah=st.origin_havdalah,
                buffer_minutes=st.buffer_minutes,
                summary=f"{prefix}{st.summary}",
                details=all_details
            )

    # Otherwise all SAFE
    is_shabbos = any(s.is_shabbos_flight for s in leg_statuses)
    return ShabbosStatus(
        level=ShabbosComplianceLevel.SAFE,
        is_shabbos_flight=is_shabbos,
        summary="All Legs Shabbos-Safe",
        details=all_details
    )
