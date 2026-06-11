import React, { useState } from 'react';
import axios from 'axios';
import ResultsGrid from './ResultsGrid';

interface Leg {
  from: string;
  to: string;
  date: string; // YYYY-MM-DD
}

export default function SearchForm() {
  const [legs, setLegs] = useState<Leg[]>([{ from: '', to: '', date: '' }]);
  const [shabbat, setShabbat] = useState(false);
  const [diet, setDiet] = useState('none');
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const addLeg = () => {
    setLegs([...legs, { from: '', to: '', date: '' }]);
  };

  const updateLeg = (index: number, field: keyof Leg, value: string) => {
    const newLegs = legs.slice();
    newLegs[index][field] = value;
    setLegs(newLegs);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('/api/search', {
        legs,
        filters: { shabbat, diet },
      });
      setResults(response.data);
    } catch (err) {
      console.error(err);
      setResults({ error: 'Search failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Flight Search</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        {legs.map((leg, i) => (
          <div key={i} className="grid grid-cols-1 md:grid-cols-3 gap-2 p-2 border rounded">
            <input
              className="border p-2 rounded"
              placeholder="From (e.g. LON)"
              value={leg.from}
              onChange={e => updateLeg(i, 'from', e.target.value.toUpperCase())}
              required
            />
            <input
              className="border p-2 rounded"
              placeholder="To (e.g. TLV)"
              value={leg.to}
              onChange={e => updateLeg(i, 'to', e.target.value.toUpperCase())}
              required
            />
            <input
              type="date"
              className="border p-2 rounded"
              value={leg.date}
              onChange={e => updateLeg(i, 'date', e.target.value)}
              required
            />
          </div>
        ))}
        <button type="button" onClick={addLeg} className="bg-amber-500 text-white px-4 py-2 rounded">
          Add Leg
        </button>
        <div className="flex items-center space-x-4">
          <label className="flex items-center">
            <input type="checkbox" checked={shabbat} onChange={e => setShabbat(e.target.checked)} className="mr-2" />
            Shabbat safe
          </label>
          <label>
            Dietary:
            <select value={diet} onChange={e => setDiet(e.target.value)} className="ml-2 border p-1 rounded">
              <option value="none">None</option>
              <option value="kosher">Kosher</option>
              <option value="halal">Halal</option>
              <option value="vegan">Vegan</option>
            </select>
          </label>
        </div>
        <button type="submit" disabled={loading} className="bg-indigo-600 text-white px-4 py-2 rounded">
          {loading ? 'Searching…' : 'Search'}
        </button>
      </form>
      {results && results.results && (
        <div className="mt-4">
          <ResultsGrid results={results.results} />
        </div>
      )}
    </div>
  );
}
