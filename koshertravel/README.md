# AeroScrape: Professional Flight Price Scraper & Jewish Travel Compliance Engine

**AeroScrape** is an agentic, multi-provider flight search engine and price scraper built in Python 3. It combines modern scraping architecture with specialized **Jewish travel compliance** tools: an astronomical **Shabbos & Yom Tov Alert System** and an authoritative **Kosher Meal (KSML / SKML) Kashrut Directory**.

---

## 🌟 Architectural Features

### 1. Universal Carrier Scraping & Kosher Food Guidance (`aeroscrape/compliance/kosher.py`)
- **Scrapes All Airlines by Default**: AeroScrape searches **any airline**—from full-service flag carriers (El Al, BA, United, Delta, Lufthansa) to low-cost carriers (Wizz Air, easyJet, Ryanair, Spirit).
- **Default Kosher Food Handling**:
  - When an airline **offers Kosher meals (KSML or Mehadrin Badatz SKML)**, the option is highlighted and checked by default (`✔ Kosher KSML (24h notice)` or `★ Mehadrin Badatz SKML`).
  - When an airline **DOES NOT offer Kosher food**, the flight is still shown (often at a lower fare!), but a prominent warning is displayed:  
    **`⚠️ No Kosher Meal – Bring Kosher food with you!`**
- **Optional Filter**: A checkbox is provided (`Require Kosher Meal`) if you wish to hide non-kosher airlines.

### 2. "Not Recommended for Shabbos" Warnings by Default (`aeroscrape/compliance/shabbos.py`)
- **No Hidden Flights by Default**: By default, flights that arrive after Candle Lighting on Friday or depart before Havdalah on Saturday are **not hidden**.
- **Halachic Comment & Warning Badges**:
  - Problematic flights are flagged with clear warning banners:  
    **`⚠️ Not Recommended for Shabbos (Arrives after Candle Lighting)`** or **`⚠️ Not Recommended for Shabbos (Departs before Havdalah)`**
  - Safe flights display **`✔ Shabbos Safe`** along with their exact time buffer before candle lighting.
- **Optional Filter**: An unchecked-by-default checkbox (`Hide Shabbos Violations`) lets you filter out non-recommended flights whenever you choose.

### 3. Interactive Trip Type Picker: One-Way, Round-Trip & Multi-City (`aeroscrape/models.py`)
- **Segmented Trip Picker Control**: Switch between **`→ One-Way`**, **`⇆ Round-Trip`**, and **`↗↘ Multi-City`** trips in both the UI and backend engine.
- **Dynamic Multi-City Itinerary Builder**: When **Multi-City** is selected, an interactive hop builder opens where you can add up to 5 consecutive flight legs (e.g., Hop 1: JFK→LHR, Hop 2: LHR→CDG, Hop 3: CDG→TLV), each with its own origin, destination, and departure date.
- **Unified Halachic & Kashrut Multi-Leg Verification**: Whether you book a One-Way, Round-Trip, or a 5-hop Multi-City itinerary, our compliance engine evaluates **every single hop** for Shabbos candle-lighting arrival buffers, Havdalah departure rules, and airline KSML policies.

### 4. Smart Autocomplete & Metropolitan City Area Expansion (`aeroscrape/airports.py`)
- **Professional Autofill & Autocomplete**: Just like in major travel apps (Google Flights, Skyscanner, Kayak), typing a city name (e.g., `New York`, `London`, `Paris`, `Miami`) immediately presents an interactive dropdown grouped into:
  - **Metropolitan City Option (`ALL AIRPORTS`)** 🏙️: e.g., `New York (NYC) - All Airports (JFK, EWR, LGA)`.
  - **Specific Airport Options (`AIRPORT`)** ✈️: e.g., `John F. Kennedy International Airport (JFK)`, `Newark Liberty International Airport (EWR)`, `LaGuardia Airport (LGA)`.
- **Automatic Multi-Airport Expansion**: Selecting a general city code (`NYC`, `LON`, `PAR`, `TYO`, `MIL`, `MIA_ALL`) automatically expands the search across all member airports in that metropolitan area, aggregating and deduplicating to show the absolute cheapest and best-value itineraries across the entire region.

### 5. Multi-Provider Meta-Scraper Engine (`aeroscrape/scrapers/`)
- **Google Flights Adapter (`GoogleFlightsScraper`)**: Fast query generation and realistic pricing models for global routes and flag carriers.
- **Skyscanner / OTA Aggregator Adapter (`SkyscannerScraper`)**: Scrapes competitive 1-stop deals and international routing alternatives.
- **Direct Airline Official Adapter (`DirectAirlineScraper`)**: Queries official airline booking systems (e.g., El Al, United, Delta, British Airways, Lufthansa) to identify direct web fares without third-party OTA fees.
- **Smart Deduplication & Value Score Algorithm**: Combines results across providers, deduplicates identical itineraries (keeping the cheapest fare), and assigns an intelligent **Value Score (0–100)** based on fare price, duration, stops, Shabbos safety, and Mehadrin kosher meal availability.

### 6. Dedicated Shabbos & Yom Tov Alert System (`aeroscrape/compliance/shabbos.py`)
- **Precision Zmanim Calculation Engine**: Computes exact astronomical Sunset, **Candle Lighting** (standard 18m / Jerusalem 40m offset), and **Havdalah** (50m after sunset / 8.5° solar depression angle) for any airport worldwide using solar declination and equation-of-time algorithms.
- **Automated Itinerary Validator**:
  - **Friday Arrivals**: Checks if a flight lands after Shabbos starts (`✖ SHABBOS VIOLATION`). If it lands before Candle Lighting, it computes the exact buffer and alerts if the buffer is under the recommended safety margin (`⚠ TIGHT BUFFER WARNING` vs. `✔ SAFE`).
  - **Saturday Departures (Motzei Shabbos)**: Verifies that flights depart comfortably after Havdalah so that airport check-in and travel do not occur on Shabbos.
  - **Overnight Flights**: Identifies airborne-during-Shabbos conflicts.
- **Custom Filtering**: Hide or display Shabbos violations via a simple flag/toggle (`--hide-violations` in CLI or UI checkbox).

### 7. Kosher Meal (KSML & SKML) Kashrut Verification (`aeroscrape/compliance/kosher.py`)
- **Authoritative 2026 Airline Database**: Includes 40+ airlines with details on:
  - Whether standard **KSML** is offered.
  - Whether **Mehadrin Badatz (SKML)** is available (e.g., El Al Badatz Edah HaChareidit, British Airways Hermolis Kedassia).
  - Required advance notice hours (0h, 24h, 48h).
  - Rabbinical supervision agency (Hermolis, Regal, MK Kosher, OU, cRc, Sohar).
- **Automated KSML Badges**: Every flight itinerary displays the airline's kosher meal policy and rating (`A+`, `A`, `B`, `C`).

---

## 🚀 Getting Started

### Installation & Environment
AeroScrape is built with Python 3 and modern standard packages:
```bash
pip install fastapi uvicorn requests beautifulsoup4 pydantic pytest rich
```

### 1. Running the Command-Line Interface (CLI)
Run searches directly from your terminal with rich colored tables, Shabbos alert statuses, and KSML guides:
```bash
# Search flights from New York City (NYC - all airports JFK, EWR, LGA) to Tel Aviv (TLV) on Friday Aug 14, 2026
PYTHONPATH=/home/user python3 /home/user/aeroscrape/cli.py --origin NYC --dest TLV --date 2026-08-14

# Optionally hide flights that are not recommended for Shabbos
PYTHONPATH=/home/user python3 /home/user/aeroscrape/cli.py --origin JFK --dest TLV --date 2026-08-14 --hide-violations

# Optionally filter for airlines offering Kosher meals (KSML) only
PYTHONPATH=/home/user python3 /home/user/aeroscrape/cli.py --origin JFK --dest LHR --date 2026-08-20 --require-ksml
```

### 2. Running the Live FastAPI Web Dashboard
Start the REST API and live Web UI server:
```bash
PYTHONPATH=/home/user uvicorn aeroscrape.web.app:app --host 0.0.0.0 --port 8000 --reload
```
- Open `http://localhost:8000/` in your browser.
- API Documentation available at `http://localhost:8000/docs`.

### 3. Previewing the Standalone Interactive Dashboard
A standalone HTML dashboard is saved at `/home/user/sample_dashboard.html`. It can be viewed immediately in any browser or preview viewer with zero backend dependency—featuring interactive filtering, One-Way/Round-Trip/Multi-City trip pickers, city/airport autocomplete, Shabbos zmanim calculations, and the complete kosher airline directory.

---

## 🧪 Running Automated Unit Tests
A comprehensive test suite is included in `/home/user/aeroscrape/tests/`:
```bash
PYTHONPATH=/home/user pytest -v /home/user/aeroscrape/tests/
```
All 8 core tests verify Zmanim astronomical math, Shabbos arrival violations, kosher meal directories, multi-scraper deduplication, city area code expansion, and One-Way/Round-Trip/Multi-City trip types.
