# AeroScrape: 1-Click Vercel Serverless Deployment Guide

Your GitHub repository **`neobankdwaas-dev/KosherTravel`** is now **100% configured for Vercel Serverless Python deployment**. We have added `api/index.py` and `vercel.json` to root so Vercel can run your FastAPI backend and Tailwind CSS interactive dashboard with zero server maintenance.

---

## 🚀 Step-by-Step: How to Deploy to Vercel in 60 Seconds

### Step 1: Import Your GitHub Repository on Vercel
1. Go to **[https://vercel.com/new](https://vercel.com/new)** and sign in with your GitHub account.
2. Under **"Import Git Repository"**, locate **`neobankdwaas-dev/KosherTravel`** and click **Import**.
   *(If you don't see it, click "Configure GitHub App" to give Vercel permission to read your private repository).*

### Step 2: Configure Environment Variables (Optional)
Because we already embedded your Marker ID **`760438`** in the repository defaults, you can deploy immediately. However, if you want to add optional live API keys in Vercel:
1. Open **Environment Variables** in the Vercel deploy screen.
2. Add:
   - `TRAVELPAYOUTS_MARKER` = `760438`
   - `AFFILIATE_NETWORK` = `travelpayouts`
   - `SERPAPI_KEY` = `your_serpapi_key` *(optional for live Google Flights)*
   - `AMADEUS_CLIENT_ID` / `AMADEUS_CLIENT_SECRET` *(optional for live Amadeus GDS)*

### Step 3: Click "Deploy"
1. Click **Deploy**.
2. Vercel will install your Python packages (`fastapi`, `uvicorn`, `pydantic`, `requests`, `beautifulsoup4`, `rich`), bundle the `@vercel/python` serverless runtime, and deploy in **~30 to 45 seconds**.
3. Once finished, you will receive your live production HTTPS URL:
   ```
   https://koshertravel.vercel.app
   ```
   *(or `https://koshertravel-yourname.vercel.app`)*

---

## 🧪 How to Test Your Live Vercel Production URL

Once your Vercel deployment completes, test these endpoints on your new URL:

1. **Interactive Web Dashboard**:
   - Open **`https://koshertravel.vercel.app/`** in your browser.
   - Try searching **`NYC` → `TLV`** or **`LON` → `TLV`** to see Metropolitan City expansion.
   - Click **Select Flight →** to confirm your Travelpayouts Marker ID (`760438`) is tracking in the booking link.
2. **Verify CPA Affiliate Configuration API**:
   ```bash
   curl -s "https://koshertravel.vercel.app/api/affiliate/status"
   # Returns: {"network": "travelpayouts", "marker_id": "760438", "sub_id": "aeroscrape_web", "is_active": true}
   ```
3. **Verify Historical Route Delay Risk API**:
   ```bash
   curl -s "https://koshertravel.vercel.app/api/delay-risk?origin=JFK&destination=TLV"
   ```
4. **Verify Crowdsourced Kosher Catering Reports API**:
   ```bash
   curl -s "https://koshertravel.vercel.app/api/kosher-reports?airline=BA"
   ```
5. **Verify Autocomplete City & Airport API**:
   ```bash
   curl -s "https://koshertravel.vercel.app/api/airports/autocomplete?q=new"
   ```

---

## 🛠️ Alternative: Deploy from Terminal Using Vercel CLI

If you prefer deploying from your command line instead of the Vercel web dashboard, open your terminal in the project folder and run:
```bash
# 1. Install Vercel CLI (if not already installed)
npm i -g vercel

# 2. Deploy to production
vercel --prod
```
Vercel will prompt you to link the repository and will output your live URL in seconds.
