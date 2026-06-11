import React from 'react';

interface Flight {
  carrier: string;
  flightNo: string;
  price: number;
  bookingUrl: string;
}

interface LegResult {
  leg: { from: string; to: string; date: string };
  flights: Flight[];
}

interface Props {
  results: LegResult[];
  filters?: { shabbat?: boolean; diet?: string };
}

export default function ResultsGrid({ results, filters }: Props) {
  return (
    <div className="mt-6 space-y-6">
      {results.map((legRes, idx) => (
        <div key={idx} className="border rounded p-4">
          <h3 className="text-lg font-semibold mb-2">
            Leg {idx + 1}: {legRes.leg.from} → {legRes.leg.to} ({legRes.leg.date})
          </h3>
          {legRes.flights.length === 0 ? (
            <p className="text-gray-500">No flights found.</p>
          ) : (
            <table className="w-full table-auto">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-2 text-left">Carrier</th>
                  <th className="p-2 text-left">Flight</th>
                  <th className="p-2 text-left">Price</th>
                  <th className="p-2 text-left">Book</th>
                </tr>
              </thead>
              <tbody>
                {legRes.flights.map((f, i) => (
                  <tr key={i} className="border-t">
                    <td className="p-2">{f.carrier}</td>
                    <td className="p-2 font-mono">{f.flightNo}</td>
                    <td className="p-2">${f.price}</td>
                    <td className="p-2">
                      {/* Risk & diet badges */}
                      {filters?.shabbat ? (
                        <span className="px-1 py-0.5 bg-rose-200 text-rose-800 rounded text-xs">Shabbat ⚠️</span>
                      ) : (
                        <span className="px-1 py-0.5 bg-emerald-200 text-emerald-800 rounded text-xs">OK</span>
                      )}
                      {filters?.diet && filters.diet !== 'none' && (
                        <span className="ml-1 px-1 py-0.5 bg-blue-200 text-blue-800 rounded text-xs">
              </tbody>
            </table>
          )}
        </div>
      ))}
    </div>
  );
}
