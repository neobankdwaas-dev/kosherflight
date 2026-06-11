import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

ddotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Health check
app.get('/api/health', (req, res) => {
  res.json({status: 'ok'});
});

import { googleSearch, extractFlightsFromUrls } from './lib/search';

// Search endpoint – receives legs and optional filters
app.post('/api/search', async (req, res) => {
  try {
    const { legs, filters } = req.body; // legs: [{from,to,date}]
    if (!Array.isArray(legs) || legs.length === 0) {
      return res.status(400).json({ error: 'No legs provided' });
    }
    const results: any[] = [];
    for (const leg of legs) {
      const query = `${leg.from.trim()} to ${leg.to.trim()} ${leg.date} flight`;
      const urls = await googleSearch(query);
      const flights = await extractFlightsFromUrls(urls);
      // Apply simple Shabbat filter if requested
      const filtered = flights.filter(f => {
        if (filters?.shabbat) {
          // naive check: exclude flights arriving after Friday sunset (placeholder)
          // Real implementation would need timezone calculations.
          return true; // keep for now
        }
        return true;
      });
      results.push({ leg, flights: filtered });
    }
    res.json({ results });
  } catch (err:any) {
    console.error('Search error', err);
    res.status(500).json({ error: err.message || 'Search failed' });
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Backend listening on http://localhost:${PORT}`);
});
