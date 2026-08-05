"""
Airport Database for AeroScrape Flight Engine and Shabbos Zmanim Calculations.
Includes IATA codes, cities, countries, timezones, latitude, longitude,
and Metropolitan City Area Codes (e.g. NYC, LON, PAR) for "All Airports" searches.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class AirportInfo(BaseModel):
    iata: str
    city: str
    country: str
    timezone: str
    lat: float
    lon: float
    name: str
    candle_lighting_offset_minutes: int = 18
    is_city_area: bool = False
    member_airports: List[str] = []


# Metropolitan City Area Codes ("All Airports" in City)
CITY_AREAS_DB: Dict[str, AirportInfo] = {
    "NYC": AirportInfo(
        iata="NYC",
        city="New York",
        country="USA",
        timezone="America/New_York",
        lat=40.7128,
        lon=-74.0060,
        name="All Airports (JFK, EWR, LGA)",
        is_city_area=True,
        member_airports=["JFK", "EWR", "LGA"]
    ),
    "LON": AirportInfo(
        iata="LON",
        city="London",
        country="UK",
        timezone="Europe/London",
        lat=51.5074,
        lon=-0.1278,
        name="All Airports (LHR, LGW)",
        is_city_area=True,
        member_airports=["LHR", "LGW"]
    ),
    "PAR": AirportInfo(
        iata="PAR",
        city="Paris",
        country="France",
        timezone="Europe/Paris",
        lat=48.8566,
        lon=2.3522,
        name="All Airports (CDG, ORY)",
        is_city_area=True,
        member_airports=["CDG", "ORY"]
    ),
    "TYO": AirportInfo(
        iata="TYO",
        city="Tokyo",
        country="Japan",
        timezone="Asia/Tokyo",
        lat=35.6762,
        lon=139.6503,
        name="All Airports (NRT, HND)",
        is_city_area=True,
        member_airports=["NRT"]
    ),
    "MIL": AirportInfo(
        iata="MIL",
        city="Milan",
        country="Italy",
        timezone="Europe/Rome",
        lat=45.4642,
        lon=9.1900,
        name="All Airports (MXP)",
        is_city_area=True,
        member_airports=["MXP"]
    ),
    "CHI": AirportInfo(
        iata="CHI",
        city="Chicago",
        country="USA",
        timezone="America/Chicago",
        lat=41.8781,
        lon=-87.6298,
        name="All Airports (ORD)",
        is_city_area=True,
        member_airports=["ORD"]
    ),
    "WAS": AirportInfo(
        iata="WAS",
        city="Washington",
        country="USA",
        timezone="America/New_York",
        lat=38.9072,
        lon=-77.0369,
        name="All Airports (IAD, DCA)",
        is_city_area=True,
        member_airports=["IAD"]
    ),
    "MIA_AREA": AirportInfo(
        iata="MIA_ALL",
        city="Miami / South Florida",
        country="USA",
        timezone="America/New_York",
        lat=25.7617,
        lon=-80.1918,
        name="All South Florida Airports (MIA, FLL, PBI)",
        is_city_area=True,
        member_airports=["MIA", "FLL", "PBI"]
    ),
}


# Comprehensive database of specific major international airports and Jewish travel hubs
AIRPORTS_DB: Dict[str, AirportInfo] = {
    # Israel
    "TLV": AirportInfo(iata="TLV", city="Tel Aviv", country="Israel", timezone="Asia/Jerusalem", lat=32.0114, lon=34.8867, name="Ben Gurion Airport", candle_lighting_offset_minutes=20),
    "ETH": AirportInfo(iata="ETH", city="Eilat", country="Israel", timezone="Asia/Jerusalem", lat=29.7237, lon=35.0114, name="Ramon Airport", candle_lighting_offset_minutes=20),
    
    # North America - US East Coast
    "JFK": AirportInfo(iata="JFK", city="New York", country="USA", timezone="America/New_York", lat=40.6413, lon=-73.7781, name="John F. Kennedy International Airport"),
    "EWR": AirportInfo(iata="EWR", city="Newark", country="USA", timezone="America/New_York", lat=40.6895, lon=-74.1745, name="Newark Liberty International Airport"),
    "LGA": AirportInfo(iata="LGA", city="New York", country="USA", timezone="America/New_York", lat=40.7769, lon=-73.8740, name="LaGuardia Airport"),
    "MIA": AirportInfo(iata="MIA", city="Miami", country="USA", timezone="America/New_York", lat=25.7959, lon=-80.2870, name="Miami International Airport"),
    "FLL": AirportInfo(iata="FLL", city="Fort Lauderdale", country="USA", timezone="America/New_York", lat=26.0726, lon=-80.1527, name="Fort Lauderdale-Hollywood International Airport"),
    "PBI": AirportInfo(iata="PBI", city="West Palm Beach", country="USA", timezone="America/New_York", lat=26.6832, lon=-80.0956, name="Palm Beach International Airport"),
    "BOS": AirportInfo(iata="BOS", city="Boston", country="USA", timezone="America/New_York", lat=42.3656, lon=-71.0096, name="Logan International Airport"),
    "PHL": AirportInfo(iata="PHL", city="Philadelphia", country="USA", timezone="America/New_York", lat=39.8729, lon=-75.2437, name="Philadelphia International Airport"),
    "IAD": AirportInfo(iata="IAD", city="Washington", country="USA", timezone="America/New_York", lat=38.9531, lon=-77.4565, name="Washington Dulles International Airport"),
    "ATL": AirportInfo(iata="ATL", city="Atlanta", country="USA", timezone="America/New_York", lat=33.6407, lon=-84.4277, name="Hartsfield-Jackson Atlanta International Airport"),

    # North America - US Central & West Coast
    "ORD": AirportInfo(iata="ORD", city="Chicago", country="USA", timezone="America/Chicago", lat=41.9742, lon=-87.9073, name="O'Hare International Airport"),
    "DFW": AirportInfo(iata="DFW", city="Dallas", country="USA", timezone="America/Chicago", lat=32.8998, lon=-97.0403, name="Dallas/Fort Worth International Airport"),
    "IAH": AirportInfo(iata="IAH", city="Houston", country="USA", timezone="America/Chicago", lat=29.9902, lon=-95.3368, name="George Bush Intercontinental Airport"),
    "DEN": AirportInfo(iata="DEN", city="Denver", country="USA", timezone="America/Denver", lat=39.8561, lon=-104.6737, name="Denver International Airport"),
    "LAX": AirportInfo(iata="LAX", city="Los Angeles", country="USA", timezone="America/Los_Angeles", lat=33.9416, lon=-118.4085, name="Los Angeles International Airport"),
    "SFO": AirportInfo(iata="SFO", city="San Francisco", country="USA", timezone="America/Los_Angeles", lat=37.6213, lon=-122.3790, name="San Francisco International Airport"),
    "SEA": AirportInfo(iata="SEA", city="Seattle", country="USA", timezone="America/Los_Angeles", lat=47.4502, lon=-122.3088, name="Seattle-Tacoma International Airport"),

    # Canada & Mexico
    "YYZ": AirportInfo(iata="YYZ", city="Toronto", country="Canada", timezone="America/Toronto", lat=43.6777, lon=-79.6248, name="Toronto Pearson International Airport"),
    "YUL": AirportInfo(iata="YUL", city="Montreal", country="Canada", timezone="America/Toronto", lat=45.4706, lon=-73.7408, name="Montreal-Pierre Elliott Trudeau International Airport"),
    "MEX": AirportInfo(iata="MEX", city="Mexico City", country="Mexico", timezone="America/Mexico_City", lat=19.4363, lon=-99.0721, name="Mexico City International Airport"),

    # Europe - Major Hubs
    "LHR": AirportInfo(iata="LHR", city="London", country="UK", timezone="Europe/London", lat=51.4700, lon=-0.4543, name="Heathrow Airport"),
    "LGW": AirportInfo(iata="LGW", city="London", country="UK", timezone="Europe/London", lat=51.1537, lon=-0.1821, name="Gatwick Airport"),
    "CDG": AirportInfo(iata="CDG", city="Paris", country="France", timezone="Europe/Paris", lat=49.0097, lon=2.5479, name="Charles de Gaulle Airport"),
    "ORY": AirportInfo(iata="ORY", city="Paris", country="France", timezone="Europe/Paris", lat=48.7262, lon=2.3652, name="Orly Airport"),
    "FRA": AirportInfo(iata="FRA", city="Frankfurt", country="Germany", timezone="Europe/Berlin", lat=50.0379, lon=8.5622, name="Frankfurt Airport"),
    "MUC": AirportInfo(iata="MUC", city="Munich", country="Germany", timezone="Europe/Berlin", lat=48.3537, lon=11.7750, name="Munich Airport"),
    "BER": AirportInfo(iata="BER", city="Berlin", country="Germany", timezone="Europe/Berlin", lat=52.3667, lon=13.5033, name="Berlin Brandenburg Airport"),
    "AMS": AirportInfo(iata="AMS", city="Amsterdam", country="Netherlands", timezone="Europe/Amsterdam", lat=52.3105, lon=4.7683, name="Amsterdam Airport Schiphol"),
    "ZRH": AirportInfo(iata="ZRH", city="Zurich", country="Switzerland", timezone="Europe/Zurich", lat=47.4647, lon=8.5492, name="Zurich Airport"),
    "GVA": AirportInfo(iata="GVA", city="Geneva", country="Switzerland", timezone="Europe/Zurich", lat=46.2370, lon=6.1092, name="Geneva Airport"),
    "VIE": AirportInfo(iata="VIE", city="Vienna", country="Austria", timezone="Europe/Vienna", lat=48.1103, lon=16.5697, name="Vienna International Airport"),
    "FCO": AirportInfo(iata="FCO", city="Rome", country="Italy", timezone="Europe/Rome", lat=41.8003, lon=12.2389, name="Leonardo da Vinci-Fiumicino Airport"),
    "MXP": AirportInfo(iata="MXP", city="Milan", country="Italy", timezone="Europe/Rome", lat=45.6306, lon=8.7281, name="Milan Malpensa Airport"),
    "MAD": AirportInfo(iata="MAD", city="Madrid", country="Spain", timezone="Europe/Madrid", lat=40.4719, lon=-3.5626, name="Adolfo Suárez Madrid-Barajas Airport"),
    "BCN": AirportInfo(iata="BCN", city="Barcelona", country="Spain", timezone="Europe/Madrid", lat=41.2974, lon=2.0833, name="Barcelona-El Prat Airport"),
    "ATH": AirportInfo(iata="ATH", city="Athens", country="Greece", timezone="Europe/Athens", lat=37.9364, lon=23.9445, name="Athens International Airport"),
    "LCA": AirportInfo(iata="LCA", city="Larnaca", country="Cyprus", timezone="Asia/Nicosia", lat=34.8751, lon=33.6249, name="Larnaca International Airport"),
    
    # Asia & Middle East
    "DXB": AirportInfo(iata="DXB", city="Dubai", country="UAE", timezone="Asia/Dubai", lat=25.2532, lon=55.3657, name="Dubai International Airport"),
    "AUH": AirportInfo(iata="AUH", city="Abu Dhabi", country="UAE", timezone="Asia/Dubai", lat=24.4330, lon=54.6511, name="Zayed International Airport"),
    "IST": AirportInfo(iata="IST", city="Istanbul", country="Turkey", timezone="Europe/Istanbul", lat=41.2753, lon=28.7519, name="Istanbul Airport"),
    "HKG": AirportInfo(iata="HKG", city="Hong Kong", country="China", timezone="Asia/Hong_Kong", lat=22.3080, lon=113.9185, name="Hong Kong International Airport"),
    "NRT": AirportInfo(iata="NRT", city="Tokyo", country="Japan", timezone="Asia/Tokyo", lat=35.7720, lon=140.3929, name="Narita International Airport"),
    "SIN": AirportInfo(iata="SIN", city="Singapore", country="Singapore", timezone="Asia/Singapore", lat=1.3644, lon=103.9915, name="Changi Airport"),
    "BKK": AirportInfo(iata="BKK", city="Bangkok", country="Thailand", timezone="Asia/Bangkok", lat=13.6900, lon=100.7501, name="Suvarnabhumi Airport"),

    # South America & Australia
    "GRU": AirportInfo(iata="GRU", city="Sao Paulo", country="Brazil", timezone="America/Sao_Paulo", lat=-23.4356, lon=-46.4731, name="Guarulhos International Airport"),
    "EZE": AirportInfo(iata="EZE", city="Buenos Aires", country="Argentina", timezone="America/Argentina/Buenos_Aires", lat=-34.8222, lon=-58.5358, name="Ezeiza International Airport"),
    "SYD": AirportInfo(iata="SYD", city="Sydney", country="Australia", timezone="Australia/Sydney", lat=-33.9461, lon=151.1772, name="Sydney Airport"),
    "MEL": AirportInfo(iata="MEL", city="Melbourne", country="Australia", timezone="Australia/Melbourne", lat=-37.6690, lon=144.8410, name="Melbourne Airport"),
}


def get_airport(iata: str) -> AirportInfo:
    """
    Retrieve AirportInfo by IATA code (case-insensitive).
    Checks both CITY_AREAS_DB (e.g. NYC, LON) and AIRPORTS_DB (e.g. JFK, LHR).
    """
    code = iata.upper().strip()
    if code in CITY_AREAS_DB:
        return CITY_AREAS_DB[code]
    if code in AIRPORTS_DB:
        return AIRPORTS_DB[code]
    
    return AirportInfo(
        iata=code,
        city=f"City ({code})",
        country="International",
        timezone="UTC",
        lat=32.0,
        lon=0.0,
        name=f"Airport ({code})",
        candle_lighting_offset_minutes=18
    )


def expand_city_to_airports(iata_code: str) -> List[str]:
    """
    If iata_code is a city area code (e.g. NYC, LON, PAR), return all member airport codes.
    Otherwise return a list containing just the single airport code.
    """
    code = iata_code.upper().strip()
    if code in CITY_AREAS_DB:
        return CITY_AREAS_DB[code].member_airports
    return [code]


def search_airports(query: str) -> List[Dict[str, Any]]:
    """
    Search airports and metropolitan city areas by name, code, city, or country.
    Returns structured suggestions grouped by city areas first, then specific airports.
    """
    q = query.strip().lower()
    results = []

    # 1. First check City Area Codes (All Airports options)
    for code, info in CITY_AREAS_DB.items():
        if (
            q in code.lower()
            or q in info.city.lower()
            or q in info.country.lower()
            or q in info.name.lower()
        ):
            results.append({
                "code": info.iata,
                "city": info.city,
                "country": info.country,
                "name": info.name,
                "type": "city",  # "city" indicates "All Airports in City"
                "members": info.member_airports
            })

    # 2. Then check Specific Airports
    for code, info in AIRPORTS_DB.items():
        if (
            q in code.lower()
            or q in info.city.lower()
            or q in info.country.lower()
            or q in info.name.lower()
        ):
            results.append({
                "code": info.iata,
                "city": info.city,
                "country": info.country,
                "name": info.name,
                "type": "airport",
                "members": [info.iata]
            })

    return results


def list_all_airports() -> Dict[str, Any]:
    """Returns all city areas and specific airports for UI initialization."""
    combined = {}
    for k, v in CITY_AREAS_DB.items():
        combined[k] = v.model_dump()
    for k, v in AIRPORTS_DB.items():
        combined[k] = v.model_dump()
    return combined
