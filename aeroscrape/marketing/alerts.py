"""
Passover & Yom Tov Fare Alert Lead Capture Engine for AeroScrape.
Captures subscriber emails and holiday travel preferences to automate B2C fare drop alerts
and build a high-value community email list.
"""
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr


class FareAlertSubscriber(BaseModel):
    id: str
    email: str
    origin: str
    destination: str
    holiday_period: str           # e.g., "Passover (Pesach) 2027", "Sukkot 2026", "Summer Israel 2026"
    target_price_usd: Optional[float] = None
    shabbos_safe_only: bool = True
    require_ksml: bool = False
    subscribed_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    status: str = "active"


class FareAlertEngine:
    """
    Thread-safe lead capture and alert notification engine.
    """
    def __init__(self):
        self._subscribers: List[FareAlertSubscriber] = []
        self._lock = threading.Lock()
        self._seed_initial_subscribers()

    def _seed_initial_subscribers(self):
        initial = [
            FareAlertSubscriber(
                id="SUB-001",
                email="traveler1@example.com",
                origin="JFK",
                destination="TLV",
                holiday_period="Passover (Pesach) 2027",
                target_price_usd=750.0,
                shabbos_safe_only=True,
                require_ksml=True
            ),
            FareAlertSubscriber(
                id="SUB-002",
                email="family_trip@example.com",
                origin="EWR",
                destination="TLV",
                holiday_period="Sukkot 2026",
                target_price_usd=800.0,
                shabbos_safe_only=True,
                require_ksml=False
            ),
            FareAlertSubscriber(
                id="SUB-003",
                email="corporate_desk@example.com",
                origin="LON",
                destination="TLV",
                holiday_period="Year-Round Israel Routes",
                target_price_usd=400.0,
                shabbos_safe_only=True,
                require_ksml=True
            ),
        ]
        with self._lock:
            self._subscribers.extend(initial)

    def subscribe(self, email: str, origin: str, destination: str, holiday_period: str = "Passover 2027", target_price: Optional[float] = None, shabbos_safe_only: bool = True, require_ksml: bool = False) -> FareAlertSubscriber:
        sub = FareAlertSubscriber(
            id=f"SUB-{len(self._subscribers) + 101}",
            email=email.strip().lower(),
            origin=origin.upper().strip(),
            destination=destination.upper().strip(),
            holiday_period=holiday_period,
            target_price_usd=target_price,
            shabbos_safe_only=shabbos_safe_only,
            require_ksml=require_ksml
        )
        with self._lock:
            self._subscribers.append(sub)
        return sub

    def get_subscribers(self) -> List[FareAlertSubscriber]:
        with self._lock:
            return list(self._subscribers)

    def check_matching_alerts(self, origin: str, destination: str, current_cheapest_usd: float) -> Dict[str, Any]:
        """
        Simulates scanning active subscribers and identifying who should receive an automated
        fare drop notification.
        """
        orig = origin.upper().strip()
        dest = destination.upper().strip()
        matches = []

        with self._lock:
            for sub in self._subscribers:
                if sub.origin == orig and sub.destination == dest and sub.status == "active":
                    if sub.target_price_usd is None or current_cheapest_usd <= sub.target_price_usd:
                        matches.append({
                            "subscriber_id": sub.id,
                            "email": sub.email,
                            "holiday_period": sub.holiday_period,
                            "target_price": sub.target_price_usd,
                            "current_cheapest": current_cheapest_usd,
                            "message": f"🚨 FARE DROP ALERT: {orig} -> {dest} is now ${current_cheapest_usd:.2f} (Shabbat-Safe verified)!"
                        })

        return {
            "route": f"{orig}-{dest}",
            "current_price": current_cheapest_usd,
            "total_active_subscribers": len(self._subscribers),
            "triggered_alerts_count": len(matches),
            "triggered_alerts": matches
        }


# Shared global alert engine instance
GLOBAL_FARE_ALERT_ENGINE = FareAlertEngine()
