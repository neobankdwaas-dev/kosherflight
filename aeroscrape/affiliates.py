"""
Automated Affiliate CPA Tracking & Deep-Link Generation Engine for AeroScrape.
Converts flight itineraries into monetized affiliate booking URLs for:
1. Travelpayouts (Aviasales, WayAway, Expedia, Kiwi)
2. Skyscanner Affiliate Partners
3. Duffel / Direct Airline Affiliate Programs
"""
import os
import urllib.parse
from typing import Optional, Dict, Any
from pydantic import BaseModel
from aeroscrape.config import load_env_file, DEFAULT_MARKER_ID, DEFAULT_AFFILIATE_NETWORK, DEFAULT_SUB_ID


class AffiliateConfig(BaseModel):
    network: str = "travelpayouts"  # "travelpayouts", "skyscanner", "kiwi", "none"
    marker_id: str = ""             # e.g. "123456" from Travelpayouts
    sub_id: str = "aeroscrape"      # Custom sub-tracking tag (e.g. "shabbos_safe", "pesach_2027")
    is_active: bool = False


class AffiliateLinkEngine:
    """
    Generates monetized booking URLs with automated CPA tracking IDs.
    """
    def __init__(self, marker_id: Optional[str] = None, network: Optional[str] = None):
        load_env_file()
        self.marker_id = marker_id or os.getenv("TRAVELPAYOUTS_MARKER", "760438")
        self.network = (network or os.getenv("AFFILIATE_NETWORK", DEFAULT_AFFILIATE_NETWORK)).lower()
        self.sub_id = os.getenv("AFFILIATE_SUB_ID", DEFAULT_SUB_ID)

    def get_config(self) -> AffiliateConfig:
        return AffiliateConfig(
            network=self.network,
            marker_id=self.marker_id or "760438",
            sub_id=self.sub_id,
            is_active=bool(self.marker_id and self.marker_id.strip() != "")
        )

    def set_marker(self, marker_id: str, network: str = "travelpayouts"):
        self.marker_id = marker_id.strip()
        self.network = network.lower().strip()

    def generate_url(
        self,
        origin: str,
        destination: str,
        date: str,
        return_date: Optional[str] = None,
        airline_code: Optional[str] = None,
        flight_number: Optional[str] = None,
        passengers: int = 1,
        cabin_class: str = "economy"
    ) -> str:
        """
        Returns an affiliate tracking deep-link for the flight itinerary.
        If no marker_id is configured, returns a standard direct flight search URL.
        """
        orig = origin.upper().strip()
        dest = destination.upper().strip()

        # 1. Travelpayouts (Aviasales / WayAway / Kiwi aggregator)
        if self.network == "travelpayouts" and self.marker_id:
            try:
                parts = date.split("-")  # YYYY-MM-DD
                ddmm = f"{parts[2]}{parts[1]}"
            except Exception:
                ddmm = "1408"
            
            route_slug = f"{orig}{ddmm}{dest}"
            if return_date and return_date.strip() != "":
                try:
                    r_parts = return_date.split("-")
                    route_slug += f"{r_parts[2]}{r_parts[1]}"
                except Exception:
                    pass
            route_slug += f"{passengers}"
            
            target_url = f"https://www.aviasales.com/search/{route_slug}"
            encoded_target = urllib.parse.quote(target_url, safe="")
            
            # Official Travelpayouts redirect deep-link format
            return f"https://tp.media/r?marker={self.marker_id}.{self.sub_id}&p=4114&u={encoded_target}"

        # 2. Skyscanner Affiliate Partners
        if self.network == "skyscanner" and self.marker_id:
            base_sky = f"https://www.skyscanner.com/transport/flights/{orig}/{dest}/{date}"
            if return_date:
                base_sky += f"/{return_date}"
            return f"{base_sky}?associateid={self.marker_id}&utm_source={self.sub_id}"

        # 3. Kiwi.com Affiliate
        if self.network == "kiwi" and self.marker_id:
            kiwi_url = f"https://www.kiwi.com/en/search/results/{orig}/{dest}/{date}"
            if return_date:
                kiwi_url += f"/{return_date}"
            return f"{kiwi_url}?affilid={self.marker_id}"

        # 4. Default: Standard Google Flights Search URL
        gf_url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{orig}%20on%20{date}"
        if airline_code:
            gf_url += f"%20with%20{airline_code}"
        return gf_url


# Global shared affiliate engine instance
GLOBAL_AFFILIATE_ENGINE = AffiliateLinkEngine()
