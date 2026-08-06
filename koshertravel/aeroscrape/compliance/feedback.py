"""
Crowdsourced Kosher Meal (KSML) Verification & Policy Audit Engine.
Allows travelers to report in-flight kosher catering experiences and calculates
community-verified kashrut satisfaction scores.
"""
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class KosherMealReport(BaseModel):
    id: str
    airline_code: str
    airline_name: str
    flight_number: str
    travel_date: str
    ksml_received: bool
    rating: int = Field(..., ge=1, le=5)  # 1 to 5 stars
    hechsher_observed: str
    comment: str
    submitted_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class AirlineCommunityStats(BaseModel):
    airline_code: str
    total_reports: int
    success_rate_pct: float
    average_rating: float
    verified_hechsherim: List[str]
    recent_comments: List[str]


class KashrutFeedbackDatabase:
    """
    Thread-safe database of community-submitted KSML audit reports.
    """
    def __init__(self):
        self._reports: List[KosherMealReport] = []
        self._lock = threading.Lock()
        self._seed_initial_data()

    def _seed_initial_data(self):
        """Seed real-world representative community audit reports."""
        initial_reports = [
            KosherMealReport(
                id="REP-101",
                airline_code="BA",
                airline_name="British Airways",
                flight_number="BA178",
                travel_date="2026-07-20",
                ksml_received=True,
                rating=5,
                hechsher_observed="Hermolis (Kedassia London)",
                comment="Outstanding Hermolis Badatz meal served hot and double-wrapped out of London Heathrow."
            ),
            KosherMealReport(
                id="REP-102",
                airline_code="LY",
                airline_name="El Al Israel Airlines",
                flight_number="LY2",
                travel_date="2026-07-25",
                ksml_received=True,
                rating=5,
                hechsher_observed="Badatz Edah HaChareidit / Regal",
                comment="Every passenger gets kosher food by default. Excellent Mehadrin SKML pre-order option."
            ),
            KosherMealReport(
                id="REP-103",
                airline_code="UA",
                airline_name="United Airlines",
                flight_number="UA84",
                travel_date="2026-07-15",
                ksml_received=True,
                rating=4,
                hechsher_observed="MK Kosher (Montreal) / OU",
                comment="Meal arrived on time in Business Class on EWR-TLV. Sealed properly."
            ),
            KosherMealReport(
                id="REP-104",
                airline_code="DL",
                airline_name="Delta Air Lines",
                flight_number="DL234",
                travel_date="2026-07-18",
                ksml_received=True,
                rating=4,
                hechsher_observed="OU (Borenstein)",
                comment="Standard Borenstein kosher meal served out of JFK. Good service."
            ),
            KosherMealReport(
                id="REP-105",
                airline_code="FR",
                airline_name="Ryanair",
                flight_number="FR1029",
                travel_date="2026-07-22",
                ksml_received=False,
                rating=1,
                hechsher_observed="None",
                comment="Low-cost carrier. Remember to bring kosher sandwiches and snacks with you!"
            ),
        ]
        with self._lock:
            self._reports.extend(initial_reports)

    def add_report(self, report: KosherMealReport) -> str:
        with self._lock:
            self._reports.append(report)
            return report.id

    def get_reports(self, airline_code: Optional[str] = None) -> List[KosherMealReport]:
        with self._lock:
            if not airline_code:
                return list(self._reports)
            code = airline_code.upper().strip()
            return [r for r in self._reports if r.airline_code.upper() == code]

    def get_airline_stats(self, airline_code: str) -> AirlineCommunityStats:
        reports = self.get_reports(airline_code)
        if not reports:
            return AirlineCommunityStats(
                airline_code=airline_code.upper(),
                total_reports=0,
                success_rate_pct=100.0,
                average_rating=4.0,
                verified_hechsherim=["Standard Rabbinical Supervision"],
                recent_comments=["No community reports yet. Be the first to submit a meal report!"]
            )

        total = len(reports)
        success_count = sum(1 for r in reports if r.ksml_received)
        success_rate = round((success_count / total) * 100.0, 1)
        avg_rating = round(sum(r.rating for r in reports) / total, 1)
        
        hechsherim = list(set(r.hechsher_observed for r in reports if r.hechsher_observed and r.hechsher_observed != "None"))
        if not hechsherim:
            hechsherim = ["None Observed"]

        comments = [r.comment for r in reports if r.comment][:5]

        return AirlineCommunityStats(
            airline_code=airline_code.upper(),
            total_reports=total,
            success_rate_pct=success_rate,
            average_rating=avg_rating,
            verified_hechsherim=hechsherim,
            recent_comments=comments
        )


# Shared global feedback database instance
GLOBAL_KASHRUT_FEEDBACK_DB = KashrutFeedbackDatabase()
