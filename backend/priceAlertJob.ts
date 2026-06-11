import { supabase } from './lib/db';
import { googleSearch, extractFlightsFromUrls } from './lib/search';
import webpush from 'web-push';
import dotenv from 'dotenv';

ddotenv.config();

// VAPID keys – generate once and store in env vars
const vapidPublic = process.env.VAPID_PUBLIC_KEY || '';
const vapidPrivate = process.env.VAPID_PRIVATE_KEY || '';
if (vapidPublic && vapidPrivate) {
  webpush.setVapidDetails('mailto:no-reply@kosherflight.dev', vapidPublic, vapidPrivate);
}

async function checkAlerts() {
  const { data: alerts, error } = await supabase.from('price_alerts').select('*');
  if (error) {
    console.error('Failed to fetch alerts', error);
    return;
  }
  if (!alerts) return;

  for (const alert of alerts as any[]) {
    const query = `${alert.origin} to ${alert.destination} flight`;
    try {
      const urls = await googleSearch(query);
      const flights = await extractFlightsFromUrls(urls);
      if (flights.length === 0) continue;
      const cheapest = flights.reduce((a, b) => (a.price < b.price ? a : b));
      if (cheapest.price <= parseFloat(alert.target_price)) {
        // Send push if subscription exists
        const { data: subs } = await supabase
          .from('push_subscriptions')
          .select('*')
          .eq('user_id', alert.user_id);
        if (subs && vapidPublic) {
          const payload = JSON.stringify({
            title: 'Price Drop Alert 🚀',
            body: `Flight ${cheapest.flightNo} ${alert.origin}→${alert.destination} now $${cheapest.price}`,
            url: cheapest.bookingUrl,
          });
          for (const sub of subs as any[]) {
            try {
              await webpush.sendNotification(sub.subscription, payload);
            } catch (e) {
              console.error('Push failed', e);
            }
          }
        }
        // Update last_notified_at
        await supabase
          .from('price_alerts')
          .update({ last_notified_at: new Date().toISOString() })
          .eq('id', alert.id);
      }
    } catch (e) {
      console.error('Alert check error', e);
    }
  }
}

// Entry point for Vercel cron
export default async function handler() {
  await checkAlerts();
  return { status: 'ok' };
}
