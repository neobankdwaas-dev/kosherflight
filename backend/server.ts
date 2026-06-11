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

// Placeholder for search endpoint
app.post('/api/search', (req, res) => {
  // TODO: integrate Gemini grounding & real scraping
  res.json({message: 'search endpoint not implemented yet'});
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Backend listening on http://localhost:${PORT}`);
});
