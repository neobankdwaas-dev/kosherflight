import fetch from 'node-fetch';
import dotenv from 'dotenv';

ddotenv.config();

const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY;
const GOOGLE_CSE_ID = process.env.GOOGLE_CSE_ID;

/**
 * Perform a Google Custom Search for the given query and return the top result URLs.
 * This is a simple wrapper; real implementation should handle pagination and rate limits.
 */
export async function googleSearch(query: string): Promise<string[]> {
  if (!GOOGLE_API_KEY || !GOOGLE_CSE_ID) {
    throw new Error('Google API credentials not configured');
  }
  const url = `https://www.googleapis.com/customsearch/v1?key=${GOOGLE_API_KEY}&cx=${GOOGLE_CSE_ID}&q=${encodeURIComponent(query)}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Google search failed: ${res.status}`);
  }
  const data = await res.json();
  const links: string[] = (data.items || []).map((item: any) => item.link);
  return links;
}

/**
 * Very naive flight data extractor – given a list of URLs it attempts to find
 * patterns that look like flight numbers and prices. In production you would
 * implement proper HTML parsing per airline site.
 */
export async function extractFlightsFromUrls(urls: string[]): Promise<any[]> {
  const flights: any[] = [];
  const flightRegex = /([A-Z]{2}\s?\d{1,4})/g; // e.g. "BA 165"
  const priceRegex = /\$?([0-9]{1,5}(?:\.[0-9]{2})?)/g;
  for (const url of urls) {
    try {
      const html = await (await fetch(url)).text();
      const flightMatches = Array.from(html.matchAll(flightRegex)).map(m => m[1]);
      const priceMatches = Array.from(html.matchAll(priceRegex)).map(m => parseFloat(m[1]));
      // Combine first flight with first price as a heuristic
      if (flightMatches.length && priceMatches.length) {
        flights.push({
          carrier: flightMatches[0].split(' ')[0],
          flightNo: flightMatches[0].replace(/\s+/g, ' '),
          price: priceMatches[0],
          bookingUrl: url,
        });
      }
    } catch (e) {
      // ignore individual failures – continue with others
    }
  }
  return flights;
}
