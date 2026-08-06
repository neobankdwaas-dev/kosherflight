# AeroScrape: Multi-Network Travel Affiliate Guide

You are not limited to Aviasales / Travelpayouts! **AeroScrape is architected to support 4 major international affiliate networks**, allowing you to maximize your commission earnings across different regions and travel styles.

---

## 1. Supported Affiliate Networks in AeroScrape (`aeroscrape/affiliates.py`)

| Network | Best For | Commission / Payout | How to Enroll |
| :--- | :--- | :--- | :--- |
| **1. Travelpayouts / Aviasales** *(Current)* | Global flights, low-cost combos, Russian/European/Americas traffic | **1.5% - 4.0%** ($5 - $30+ per ticket) | **Active (`Marker 760438`)** at `travelpayouts.com` |
| **2. Skyscanner Affiliate Partners** | UK, European, and US flight comparisons | **20% - 50% of Skyscanner's revenue share** | Apply via **CJ Affiliate (cj.com)** or **Awin.com** (Search "Skyscanner") |
| **3. Kiwi.com Affiliate Program** | "Hacker Fares", multi-city virtual interlining, student/budget travelers | **3.0% CPA** per booking | Register at **`partners.kiwi.com`** or enable inside Travelpayouts |
| **4. Expedia / Booking.com Partners** | Corporate travel, bundled Flight + Hotel packages | **2.0% - 6.0%** total booking value | Apply at **`expediagroup.com/partners`** or enable inside Travelpayouts |

---

## 2. What Do You Need to Affiliate With Them?

1. **Your Live Website URL**:  
   You already have this! Provide **`https://koshertravel.vercel.app`** when submitting your partner applications.
2. **Payout Information**:  
   A PayPal email address or Bank account (IBAN / Routing number) to receive monthly disbursements.
3. **Tax Documentation**:  
   Standard W-9 (for US residents) or W-8BEN (for international residents) form completed digitally on the partner network's tax portal.

---

## 3. How to Switch or Enable Another Network in AeroScrape

You can switch your active affiliate tracking network in AeroScrape anytime using environment variables or our REST API:

### Option A: Via Environment Variables (in Vercel Settings or `.env`)
```bash
# To switch to Skyscanner Affiliate
export AFFILIATE_NETWORK="skyscanner"
export TRAVELPAYOUTS_MARKER="your_skyscanner_partner_id"

# To switch to Kiwi.com Affiliate
export AFFILIATE_NETWORK="kiwi"
export TRAVELPAYOUTS_MARKER="your_kiwi_affiliate_id"
```

### Option B: Dynamically via REST API (Zero Restart Required)
```bash
# Switch to Skyscanner live
curl -X POST "https://koshertravel.vercel.app/api/affiliate/config?marker_id=YOUR_SKYSCANNER_ID&network=skyscanner"

# Revert to Travelpayouts (Marker 760438)
curl -X POST "https://koshertravel.vercel.app/api/affiliate/config?marker_id=760438&network=travelpayouts"
```

---

## Pro-Tip: You Can Enable Kiwi, Expedia, and Booking.com Inside Travelpayouts!
Because you already have a verified **Travelpayouts** account (`Marker 760438`), **you do not need to open separate accounts or bank portals for Kiwi, Expedia, or Booking.com!**

Inside your Travelpayouts dashboard (**`www.travelpayouts.com/programs`**):
1. Search for **"Kiwi.com"**, **"Expedia"**, **"Trip.com"**, or **"Booking.com"**.
2. Click **"Connect"** — approval is instant.
3. All earnings across Aviasales, Kiwi, and Expedia will pool together into your single monthly Travelpayouts PayPal/bank disbursement.
