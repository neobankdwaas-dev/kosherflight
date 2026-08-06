"""
Automated Itinerary Share Generator for AeroScrape.
Generates WhatsApp-ready and printable text summaries with monetized affiliate links
for easy sharing with family, Passover groups, or rabbis.
"""
import urllib.parse
from typing import Dict, Any
from aeroscrape.models import FlightResult
from aeroscrape.affiliates import GLOBAL_AFFILIATE_ENGINE


def generate_share_summary(flight: FlightResult) -> Dict[str, str]:
    """
    Generates a clean text summary and a direct WhatsApp click-to-chat URL
    containing the monetized Travelpayouts affiliate booking link.
    """
    leg = flight.outbound_leg
    dep_date = leg.departure_time.strftime("%A, %b %d, %Y")
    dep_time = leg.departure_time.strftime("%H:%M")
    arr_time = leg.arrival_time.strftime("%H:%M")

    sh_text = "🕯️ Shabbos Safe Itinerary"
    if flight.shabbos_status:
        if flight.shabbos_status.level == "WARNING":
            sh_text = f"⚠ Tight Shabbos Buffer ({flight.shabbos_status.summary})"
        elif flight.shabbos_status.level == "VIOLATION":
            sh_text = f"⚠️ Not Recommended for Shabbos ({flight.shabbos_status.summary})"

    ko_text = "⚠️ No Kosher Meal - Bring Kosher food with you!"
    if flight.kosher_info:
        if flight.kosher_info.mehadrin_skml_offered:
            ko_text = f"★ Mehadrin Badatz SKML Offered ({flight.kosher_info.advance_notice_hours}h notice)"
        elif flight.kosher_info.ksml_offered:
            ko_text = f"✔ Kosher KSML Available ({flight.kosher_info.advance_notice_hours}h notice)"

    text_lines = [
        "✈️ AeroScrape Shabbat-Safe & Kosher Flight Deal",
        f"Route: {leg.origin_city} ({leg.origin}) ➔ {leg.destination_city} ({leg.destination})",
        f"Date: {dep_date} ({dep_time} - {arr_time})",
        f"Airline: {leg.airline_name} ({leg.flight_number}) • {leg.aircraft}",
        f"Stops: {'Non-stop' if leg.stops == 0 else f'{leg.stops} Stop ({', '.join(leg.stop_airports)})'}",
        f"Price: ${flight.price.total_price:.2f} (Value Score: {flight.value_score}/100)",
        f"{sh_text}",
        f"{ko_text}",
        f"🔗 Book here: {flight.booking_url}"
    ]

    summary_text = "\n".join(text_lines)
    encoded_text = urllib.parse.quote(summary_text)
    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
    mailto_url = f"mailto:?subject=AeroScrape%20Flight%20Deal%20%24{flight.price.total_price:.2f}%20{leg.origin}-{leg.destination}&body={encoded_text}"

    return {
        "summary_text": summary_text,
        "whatsapp_url": whatsapp_url,
        "mailto_url": mailto_url,
        "booking_url": flight.booking_url
    }
