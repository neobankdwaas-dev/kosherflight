-- Supabase schema for KosherFlight

CREATE TABLE IF NOT EXISTS price_alerts (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid NOT NULL,
  origin text NOT NULL,
  destination text NOT NULL,
  target_price numeric NOT NULL,
  last_notified_at timestamptz,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS itineraries (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid NOT NULL,
  legs jsonb NOT NULL, -- [{from, to, date, flight...}]
  created_at timestamptz DEFAULT now()
);
