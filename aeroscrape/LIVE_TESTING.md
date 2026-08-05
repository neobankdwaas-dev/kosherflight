# AeroScrape: Live Testing & Real-World Execution Guide

This guide explains how to test **AeroScrape** right now inside this workspace, how to run it on your local computer, and how to connect real-time live flight data from **Google Flights**, **Skyscanner**, and **Amadeus**.

---

## 1. How to Test Right Now Inside This Workspace

### Option A: Using the Interactive Web Dashboard (Running on Port 8000)
1. Open the live preview at **`http://localhost:8000`** in your browser.
2. In the search box:
   - Try typing **`New York`** or **`NYC`** to test the Metropolitan City Area expansion.
   - Choose a target date (e.g., a Friday like `2026-08-14` or a Saturday).
   - Toggle between **`→ One-Way`**, **`⇆ Round-Trip`**, and **`↗↘ Multi-City`**.
3. Observe how:
   - **All airlines are searched by default** (including low-cost options like Wizz Air and easyJet).
   - Non-kosher flights display: **`⚠️ No Kosher Meal – Bring Kosher food with you!`**
   - Shabbos conflicts display: **`⚠️ Not Recommended for Shabbos (Arrives after Candle Lighting)`**

### Option B: Using the Command-Line Interface (CLI) in Terminal
Open a terminal in the workspace and run any of the following commands:
```bash
# Standard Round-Trip search from New York City (NYC - all airports) to Tel Aviv (TLV)
PYTHONPATH=/home/user python3 /home/user/aeroscrape/cli.py --origin NYC --dest TLV --date 2026-08-14

# Hide non-recommended Shabbos flights using the optional flag
PYTHONPATH=/home/user python3 /home/user/aeroscrape/cli.py --origin JFK --dest TLV --date 2026-08-14 --hide-violations

# Only show airlines offering Kosher meals (KSML)
PYTHONPATH=/home/user python3 /home/user/aeroscrape/cli.py --origin JFK --dest LHR --date 2026-08-20 --require-ksml
```

### Option C: Using the Standalone Interactive Deliverable
Open **`sample_dashboard.html`** in the workspace file viewer. It runs 100% client-side with full city autocomplete, One-Way/Round-Trip/Multi-City pickers, Shabbos Zmanim calculator, and Kosher airline directory.

---

## 2. How to Run AeroScrape on Your Own PC / Mac / Linux Machine

1. **Download/Clone the Code**:
   Copy the `/home/user/aeroscrape` folder to your computer.
2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the CLI or Web Server**:
   ```bash
   # Run CLI
   python3 -m aeroscrape.cli --origin JFK --dest TLV --date 2026-08-14

   # Start Web Server
   uvicorn aeroscrape.web.app:app --reload --port 8000
   ```

---

## 3. How to Run a REAL Live Flight Test (Google Flights & Amadeus APIs)

By default, AeroScrape uses a deterministic multi-carrier pricing engine so it runs reliably without third-party API keys or CAPTCHAs. To scrape **real live fares from the web**, AeroScrape includes two production live adapters in `aeroscrape/scrapers/live_adapter.py`:

### Method 1: Live Google Flights via SerpApi (Free Tier: 100 searches/month)
1. Sign up for a free API key at **[https://serpapi.com](https://serpapi.com)**.
2. Set your API key in your terminal environment:
   ```bash
   export SERPAPI_KEY="your_free_serpapi_key_here"
   ```
3. Run the CLI with the `--live` flag:
   ```bash
   PYTHONPATH=/home/user python3 /home/user/aeroscrape/cli.py --origin JFK --dest TLV --date 2026-08-14 --live
   ```
   *AeroScrape will immediately query Google Flights live JSON endpoints, pull real-time fares, schedules, airlines, and stops, and run them through the Shabbos and Kosher compliance engines.*

### Method 2: Live Airline Global Distribution System via Amadeus Free Sandbox
1. Register for a free developer account at **[https://developers.amadeus.com](https://developers.amadeus.com)**.
2. Create a Self-Service app to get your Client ID and Client Secret.
3. Set them in your environment:
   ```bash
   export AMADEUS_CLIENT_ID="your_client_id"
   export AMADEUS_CLIENT_SECRET="your_client_secret"
   ```
4. Run with the `--live` flag:
   ```bash
   PYTHONPATH=/home/user python3 /home/user/aeroscrape/cli.py --origin JFK --dest LHR --date 2026-08-14 --live
   ```

### Method 3: Direct Python Open-Source Scrapers (`fast-flights`)
If you prefer not to use any API key, you can install the open-source Google Flights scraper library:
```bash
pip install fast-flights
```
You can plug `fast-flights` directly into any custom scraper by inheriting from `FlightScraper` in `aeroscrape/scrapers/base.py` and implementing `search_flights(query)`.
