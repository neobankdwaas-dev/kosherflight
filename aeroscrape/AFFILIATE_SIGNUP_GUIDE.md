# AeroScrape: 3-Minute Affiliate Program Enrollment Guide

While I cannot automatically submit your legal name, tax identification (W-9/W-8BEN), and bank account / PayPal payout details on third-party financial platforms, **I have built and integrated the automated CPA Affiliate Tracking Engine (`aeroscrape/affiliates.py`) into your application.**

As soon as you complete the **3-minute free registration** below, you can plug your Affiliate ID into AeroScrape, and **every single flight booking link will automatically earn you a 1.5% to 4% commission ($5 to $30+ per ticket)**.

---

## Step 1: Register for Free with the #1 Travel Affiliate Platform (Travelpayouts)

**Travelpayouts** is the travel industry standard affiliate network. It aggregates **Aviasales**, **WayAway**, **Expedia**, **Booking.com**, and **Kiwi.com**, and offers **instant approval with zero traffic minimums**.

1. Go to **[https://www.travelpayouts.com/](https://www.travelpayouts.com/)** and click **"Sign Up"**.
2. Enter your email address and create a password.
3. Select **"Flights"** as your category and choose **Aviasales / WayAway** as your flight partner program.
4. On your dashboard, copy your **"Marker ID"** (a 5- or 6-digit number, e.g., `123456`).
5. Under **"Finance / Payouts"**, add your **PayPal address or Bank IBAN** so you can receive your monthly commission payments.

*(Alternative programs: You can also register for **Skyscanner Affiliate Partners** at `partners.skyscanner.net` or **Duffel API** at `duffel.com`)*

---

## Step 2: Plug Your Marker ID into AeroScrape (3 Automated Ways)

I have built three automated ways to activate your Affiliate ID in AeroScrape:

### 1. In Your Terminal / Environment Variable (Recommended for Production)
Set your Marker ID in your environment before starting the server or CLI:
```bash
export TRAVELPAYOUTS_MARKER="your_marker_id_here"
export AFFILIATE_NETWORK="travelpayouts"
```
*Now every search automatically generates monetized Travelpayouts / Aviasales booking URLs.*

### 2. Via the Live REST API Endpoint
You can dynamically update your affiliate tracking ID anytime without restarting the server:
```bash
curl -X POST "http://localhost:8000/api/affiliate/config?marker_id=YOUR_MARKER_ID&network=travelpayouts"
```

### 3. In the Python Code (`aeroscrape/affiliates.py`)
You can open `/home/user/aeroscrape/affiliates.py` and set your default marker on line 21:
```python
self.marker_id = marker_id or os.getenv("TRAVELPAYOUTS_MARKER", "YOUR_MARKER_ID")
```

---

## Step 3: Verify Your Monetized Links in Action

1. Run a flight search:
   ```bash
   PYTHONPATH=/home/user python3 /home/user/aeroscrape/cli.py --origin NYC --dest TLV --date 2026-08-14
   ```
2. Look at the generated `booking_url` for any flight:
   - **Without Marker ID**: Standard direct search link (`https://www.google.com/travel/flights?...`).
   - **With Marker ID Active**: Automated CPA deep-link:
     `https://tp.media/r?marker=YOUR_MARKER_ID.aeroscrape_web&p=4114&u=https%3A%2F%2Fwww.aviasales.com%2Fsearch%2F1408NYCTLV1`

When any traveler clicks **"Select Flight →"** on your dashboard and books a ticket, Travelpayouts attributes the commission directly to your account!
