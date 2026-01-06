import { useState } from 'react';
import { estimateTco } from './api';
import { TcoResult } from './types';
import './App.css';

function App() {
  const [make, setMake] = useState('');
  const [model, setModel] = useState('');
  const [year, setYear] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TcoResult | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await estimateTco({
        make,
        model,
        year: parseInt(year),
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="app">
      <header>
        <h1>🚗 Car Lifetime TCO Calculator</h1>
        <p>Estimate the total cost of ownership for your vehicle</p>
      </header>

      <div className="container">
        <form onSubmit={handleSubmit} className="input-form">
          <div className="form-group">
            <label htmlFor="make">Make</label>
            <input
              id="make"
              type="text"
              value={make}
              onChange={(e) => setMake(e.target.value)}
              placeholder="e.g., Honda"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="model">Model</label>
            <input
              id="model"
              type="text"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              placeholder="e.g., Civic"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="year">Year</label>
            <input
              id="year"
              type="number"
              value={year}
              onChange={(e) => setYear(e.target.value)}
              placeholder="e.g., 2016"
              min="2005"
              max="2026"
              required
            />
          </div>

          <button type="submit" disabled={loading} className="estimate-btn">
            {loading ? 'Calculating...' : 'Estimate TCO'}
          </button>
        </form>

        {error && (
          <div className="error-box">
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <div className="results">
            <div className="result-header">
              <h2>
                {result.vehicle.year} {result.vehicle.make} {result.vehicle.model}
              </h2>
              <span className={`confidence confidence-${result.confidence}`}>
                {result.confidence.toUpperCase()} CONFIDENCE
              </span>
            </div>

            <div className="summary-cards">
              <div className="card">
                <div className="card-label">Total Lifetime Cost</div>
                <div className="card-value">
                  {formatCurrency(result.lifetime.totalCost)}
                </div>
              </div>
              <div className="card">
                <div className="card-label">Cost Per Month</div>
                <div className="card-value">
                  {formatCurrency(result.lifetime.costPerMonth)}
                </div>
              </div>
              <div className="card">
                <div className="card-label">Duration</div>
                <div className="card-value">
                  {result.lifetime.months} months
                </div>
                <div className="card-sublabel">
                  ({result.lifetime.endReason === 'maxYears' ? 'Max age reached' : 'Max km reached'})
                </div>
              </div>
            </div>

            <div className="breakdown">
              <h3>Cost Breakdown</h3>
              <table>
                <tbody>
                  <tr>
                    <td>Depreciation</td>
                    <td>{formatCurrency(result.breakdown.depreciation)}</td>
                  </tr>
                  <tr>
                    <td>Fuel</td>
                    <td>{formatCurrency(result.breakdown.fuel)}</td>
                  </tr>
                  <tr>
                    <td>Maintenance</td>
                    <td>{formatCurrency(result.breakdown.maintenance)}</td>
                  </tr>
                  <tr>
                    <td>Fees (Insurance, Registration, Taxes)</td>
                    <td>{formatCurrency(result.breakdown.fees)}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="assumptions">
              <h3>Assumptions Used</h3>
              <ul>
                <li>Average km per year: {result.assumptionsUsed.kmPerYear.toLocaleString()}</li>
                <li>Fuel price per liter: ${result.assumptionsUsed.fuelPricePerLiter.toFixed(2)}</li>
                <li>Maximum vehicle age: {result.assumptionsUsed.maxYears} years</li>
                <li>Maximum km: {result.assumptionsUsed.maxKm.toLocaleString()}</li>
              </ul>
            </div>

            {result.notes && result.notes.length > 0 && (
              <div className="notes">
                <h3>Notes</h3>
                <ul>
                  {result.notes.map((note, idx) => (
                    <li key={idx}>{note}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.sourcesUsed && result.sourcesUsed.length > 0 && (
              <div className="sources">
                <h3>Sources</h3>
                {result.sourcesUsed.map((source, idx) => (
                  <div key={idx} className="source-item">
                    <a href={source.url} target="_blank" rel="noopener noreferrer">
                      {source.title}
                    </a>
                    <p>{source.snippet}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <footer>
        <p>
          ⚠️ Results are AI-generated estimates based on publicly available information.
          Actual costs may vary significantly based on individual usage, location, and vehicle condition.
        </p>
      </footer>
    </div>
  );
}

export default App;
