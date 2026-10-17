import { useState } from "react";
const API_URL = "http://127.0.0.1:8000";
type AnyResult = Record<string, unknown>;

export default function ActuarialTools() {
  const [baseline, setBaseline] = useState('{"reserve": 100000, "profit": 12000}');
  const [candidate, setCandidate] = useState('{"reserve": 108000, "profit": 10500}');
  const [threshold, setThreshold] = useState("5");
  const [sumAssured, setSumAssured] = useState("500000");
  const [probability, setProbability] = useState("0.02");
  const [expense, setExpense] = useState("10");
  const [risk, setRisk] = useState("5");
  const [start, setStart] = useState("1000000");
  const [growth, setGrowth] = useState("4");
  const [years, setYears] = useState("10");
  const [result, setResult] = useState<AnyResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function callTool(path: string, body: Record<string, unknown>) {
    setLoading(true); setError(""); setResult(null);
    try {
      const response = await fetch(`${API_URL}${path}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const payload = await response.json();
      if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "Tool request failed.");
      setResult(payload as AnyResult);
    } catch (err) { setError(err instanceof Error ? err.message : "Could not connect to ActuTrace API."); }
    finally { setLoading(false); }
  }

  return <section className="panel actuarial-tools">
    <p className="eyebrow">ACTUARIAL WORKBENCH · EXPERIMENTAL</p><h2>Additional actuarial tools</h2>
    <p className="panel-description">Explore model changes, pricing assumptions, and multi-year growth scenarios. These are educational calculations, not production actuarial models.</p>
    <div className="tool-grid">
      <article className="tool-card"><h3>1. Model Change Monitor</h3><p>Compare named output metrics from two model runs.</p>
        <label>Baseline outputs (JSON)<textarea rows={3} value={baseline} onChange={e => setBaseline(e.target.value)} /></label>
        <label>Candidate outputs (JSON)<textarea rows={3} value={candidate} onChange={e => setCandidate(e.target.value)} /></label>
        <label>Flag change threshold (%)<input type="number" min="0" max="100" value={threshold} onChange={e => setThreshold(e.target.value)} /></label>
        <button disabled={loading} onClick={() => { try { void callTool("/tools/model-monitor", { baseline: JSON.parse(baseline), candidate: JSON.parse(candidate), materiality_percent: Number(threshold) }); } catch { setError("Enter valid JSON objects for both model outputs."); } }}>Compare outputs</button>
      </article>
      <article className="tool-card"><h3>2. Pricing Scenario Simulator</h3><p>Expected claim cost plus configurable expense and risk loads.</p>
        <label>Sum assured (₹)<input type="number" min="0" value={sumAssured} onChange={e => setSumAssured(e.target.value)} /></label>
        <label>Claim probability (0–1)<input type="number" min="0" max="1" step="0.001" value={probability} onChange={e => setProbability(e.target.value)} /></label>
        <label>Expense load (%)<input type="number" min="0" max="500" value={expense} onChange={e => setExpense(e.target.value)} /></label>
        <label>Risk load (%)<input type="number" min="0" max="500" value={risk} onChange={e => setRisk(e.target.value)} /></label>
        <button disabled={loading} onClick={() => void callTool("/tools/pricing-simulator", { sum_assured: Number(sumAssured), claim_probability: Number(probability), expense_load_percent: Number(expense), risk_load_percent: Number(risk) })}>Calculate scenario</button>
      </article>
      <article className="tool-card"><h3>3. Liability Growth Projection</h3><p>Project an amount using a constant annual growth assumption.</p>
        <label>Starting amount (₹)<input type="number" min="0" value={start} onChange={e => setStart(e.target.value)} /></label>
        <label>Annual growth (%)<input type="number" min="-100" max="100" step="0.1" value={growth} onChange={e => setGrowth(e.target.value)} /></label>
        <label>Years (1–100)<input type="number" min="1" max="100" value={years} onChange={e => setYears(e.target.value)} /></label>
        <button disabled={loading} onClick={() => void callTool("/tools/liability-projection", { starting_amount: Number(start), annual_growth_percent: Number(growth), years: Number(years) })}>Project scenario</button>
      </article>
      <article className="tool-card"><h3>4. Audit & Reporting</h3><p>Download the latest run metadata, input hashes, configuration and current reports.</p>
        <a className="tool-link" href={`${API_URL}/reports/analysis_summary.json`}>Analysis audit summary (JSON) ↓</a>
        <a className="tool-link" href={`${API_URL}/reports/validation_findings.csv`}>Validation findings (CSV) ↓</a>
        <a className="tool-link" href={`${API_URL}/reports/valuation_impacts.csv`}>Valuation impacts (CSV) ↓</a>
      </article>
    </div>
    {loading && <p role="status">Calculating scenario…</p>}{error && <p className="tool-error" role="alert">{error}</p>}
    {result && <div className="tool-result"><h3>Tool result</h3><pre>{JSON.stringify(result, null, 2)}</pre></div>}
    <p className="helper-text">Pricing and liability outputs are deterministic illustrations, not approved premiums, reserves, regulatory valuations, or financial advice.</p>
  </section>;
}
