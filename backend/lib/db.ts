import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

ddotenv.config();

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  throw new Error('Supabase credentials not set');
}

export const supabase = createClient(supabaseUrl, supabaseServiceKey);

// Simple helper functions
export async function createPriceAlert(alert: {
  user_id: string;
  origin: string;
  destination: string;
  target_price: number;
}) {
  const { data, error } = await supabase.from('price_alerts').insert(alert);
  if (error) throw error;
  return data;
}

export async function getPriceAlertsByUser(userId: string) {
  const { data, error } = await supabase
    .from('price_alerts')
    .select('*')
    .eq('user_id', userId);
  if (error) throw error;
  return data;
}

export async function createItinerary(itinerary: {
  user_id: string;
  legs: any; // store as jsonb
}) {
  const { data, error } = await supabase.from('itineraries').insert(itinerary);
  if (error) throw error;
  return data;
}
