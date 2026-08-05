"""
Data models and schemas for AeroScrape Flight Engine.
"""
from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CabinClass(str, Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class TripType(str, Enum):
    ONE_WAY = "one_way"
    ROUND_TRIP = "round_trip"
    MULTI_CITY = "multi_city"


class ShabbosComplianceLevel(str, Enum):
    SAFE = "SAFE"                 # Fully compliant with comfortable buffer
    WARNING = "WARNING"           # Close to Candle Lighting / Havdalah (tight buffer)
    VIOLATION = "VIOLATION"       # Airborne during Shabbos/Yom Tov or buffer breached


class ShabbosStatus(BaseModel):
    """
    Shabbos compliance details for an itinerary.
    """
    level: ShabbosComplianceLevel
    is_shabbos_flight: bool = False
    origin_candle_lighting: Optional[datetime] = None
    dest_candle_lighting: Optional[datetime] = None
    origin_havdalah: Optional[datetime] = None
    dest_havdalah: Optional[datetime] = None
    buffer_minutes: Optional[int] = None
    summary: str
    details: List[str] = Field(default_factory=list)


class KosherMealInfo(BaseModel):
    """
    Kosher meal (KSML / SKML) policy and supervision for an airline.
    """
    airline_code: str
    airline_name: str
    ksml_offered: bool = True
    mehadrin_skml_offered: bool = False
    advance_notice_hours: int = 24
    certification: str = "Various Orthodox Hechsherim"
    notes: str = ""
    is_recommended: bool = True
    rating: str = "A"  # A+, A, B, C, N/A


class FlightLeg(BaseModel):
    """
    Represents a single directional flight leg (could be direct or have layovers).
    """
    airline_code: str
    airline_name: str
    flight_number: str
    origin: str           # IATA e.g. "JFK"
    origin_city: str      # e.g. "New York"
    destination: str      # IATA e.g. "TLV"
    destination_city: str # e.g. "Tel Aviv"
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    stops: int = 0
    stop_airports: List[str] = Field(default_factory=list)
    aircraft: str = "Boeing 787-9"
    cabin_class: CabinClass = CabinClass.ECONOMY


class PriceBreakdown(BaseModel):
    base_fare: float
    taxes_fees: float
    currency: str = "USD"
    total_price: float

    @classmethod
    def from_total(cls, total: float, currency: str = "USD") -> "PriceBreakdown":
        base = round(total * 0.82, 2)
        taxes = round(total - base, 2)
        return cls(
            base_fare=base,
            taxes_fees=taxes,
            currency=currency,
            total_price=total
        )


class FlightResult(BaseModel):
    """
    A full flight itinerary option scraped from one or more providers.
    Supports One-Way, Round-Trip, and Multi-City trips.
    """
    id: str
    scraper_source: str           # e.g., "Google Flights", "Skyscanner", "Direct Airline"
    trip_type: TripType
    outbound_leg: FlightLeg
    return_leg: Optional[FlightLeg] = None
    multi_legs: List[FlightLeg] = Field(default_factory=list) # Populated when trip_type == MULTI_CITY
    price: PriceBreakdown
    value_score: float = 0.0      # Calculated value score (0-100) based on price, stops, duration
    booking_url: str = ""
    shabbos_status: Optional[ShabbosStatus] = None
    kosher_info: Optional[KosherMealInfo] = None
    tags: List[str] = Field(default_factory=list)

    @property
    def total_duration_minutes(self) -> int:
        if self.trip_type == TripType.MULTI_CITY and self.multi_legs:
            return sum(l.duration_minutes for l in self.multi_legs)
        dur = self.outbound_leg.duration_minutes
        if self.return_leg:
            dur += self.return_leg.duration_minutes
        return dur

    @property
    def all_legs(self) -> List[FlightLeg]:
        """Returns a unified list of all flight legs in this itinerary."""
        if self.trip_type == TripType.MULTI_CITY and self.multi_legs:
            return self.multi_legs
        legs = [self.outbound_leg]
        if self.return_leg:
            legs.append(self.return_leg)
        return legs


class MultiCityLeg(BaseModel):
    """
    Represents a leg query in a multi-city search.
    """
    origin: str                   # 3-letter IATA airport code or city code
    destination: str              # 3-letter IATA airport code or city code
    departure_date: str           # YYYY-MM-DD


class FlightQuery(BaseModel):
    """
    User query for flight search.
    Supports One-Way, Round-Trip, and Multi-City.
    """
    trip_type: TripType = TripType.ROUND_TRIP
    origin: str                   # 3-letter IATA airport code or city code (e.g. NYC)
    destination: str              # 3-letter IATA airport code or city code (e.g. TLV)
    departure_date: str           # YYYY-MM-DD
    return_date: Optional[str] = None # Required if round_trip
    multi_city_legs: Optional[List[MultiCityLeg]] = None # Required if multi_city
    passengers: int = 1
    cabin_class: CabinClass = CabinClass.ECONOMY
    currency: str = "USD"
    max_stops: Optional[int] = None
    
    # Custom Compliance Filters
    shabbos_buffer_hours: float = 3.0       # Hours of buffer before candle lighting / after Havdalah
    filter_shabbos_violations: bool = False # By default FALSE: show all flights with "Not Recommended for Shabbos" comments
    require_ksml: bool = False              # By default FALSE: show all airlines and warn to bring Kosher food if not available
    preferred_hechsher: Optional[str] = None # Optional preferred kashrut standard e.g. "Badatz", "OU"


class ScraperStats(BaseModel):
    total_found: int
    cheapest_price: float
    average_price: float
    fastest_duration_minutes: int
    shabbos_safe_count: int
    kosher_available_count: int
    scrapers_queried: List[str]
    execution_time_ms: float
    cache_hit: bool = False
    delay_risk_level: str = "LOW"
    delay_risk_summary: str = "Standard punctuality profile (3.0h buffer sufficient)."
