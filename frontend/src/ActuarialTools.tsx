import { useState, type ReactNode } from "react";

const API_URL = "http://127.0.0.1:8000";

type AnyResult = Record<string, unknown>;

function formatLabel(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatValue(key: string, value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";

  if (typeof value === "number" && Number.isFinite(value)) {
    const normalizedKey = key.toLowerCase();

    if (
      /percent|percentage|growth_rate|change_rate/.test(normalizedKey)
    ) {
      return `${value.toLocaleString("en-IN", {
        maximumFractionDigits: 2,
      })}%`;
    }

    if (
      /probability|claim_probability/.test(normalizedKey) &&
      value >= 0 &&
      value <= 1
    ) {
      return value.toLocaleString("en-IN", {
        maximumFractionDigits: 4,
      });
    }

    if (
      /amount|premium|reserve|profit|liability|cost|sum_assured|expense|risk_load|expected_claim/.test(
        normalizedKey,
      )
    ) {
      return `₹${value.toLocaleString("en-IN", {
        maximumFractionDigits: 2,
      })}`;
    }

    return value.toLocaleString("en-IN", {
      maximumFractionDigits: 4,
    });
  }

  if (typeof value === "string") return value;
  if (Array.isArray(value)) return `${value.length} items`;

  return "Details available";
}

function ResultValue({
  label,
  value,
}: {
  label: string;
  value: unknown;
}): ReactNode {
  if (value === null || value === undefined) {
    return <p className="result-value">—</p>;
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return <p className="result-muted">No items to display.</p>;
    }

    if (
      value.every(
        (item) =>
          item !== null &&
          typeof item === "object" &&
          !Array.isArray(item),
      )
    ) {
      const rows = value as Record<string, unknown>[];
      const columns = Array.from(
        new Set(rows.flatMap((row) => Object.keys(row))),
      );

      return (
        <div className="result-table-wrap">
          <table className="result-table">
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>{formatLabel(column)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={index}>
                  {columns.map((column) => (
                    <td key={column}>
                      {formatValue(column, row[column])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    return (
      <ul className="result-list">
        {value.map((item, index) => (
          <li key={index}>
            {item !== null && typeof item === "object"
              ? JSON.stringify(item)
              : formatValue(label, item)}
          </li>
        ))}
      </ul>
    );
  }

  if (typeof value === "object") {
    return (
      <div className="result-nested">
        {Object.entries(value as Record<string, unknown>).map(
          ([key, nestedValue]) => (
            <div className="result-field" key={key}>
              <span className="result-label">{formatLabel(key)}</span>
              <div className="result-field-value">
                <ResultValue label={key} value={nestedValue} />
              </div>
            </div>
          ),
        )}
      </div>
    );
  }

  return <p className="result-value">{formatValue(label, value)}</p>;
}

function ResultDisplay({ result }: { result: AnyResult }) {
  const entries = Object.entries(result);
  const scalarEntries = entries.filter(
    ([, value]) =>
      value === null ||
      ["string", "number", "boolean"].includes(typeof value),
  );
  const complexEntries = entries.filter(
    ([, value]) =>
      value !== null &&
      (typeof value === "object"),
  );

  return (
    <div className="tool-result" aria-live="polite">
      <div className="result-heading">
        <div>
          <p className="eyebrow">ANALYSIS COMPLETE</p>
          <h3>Results summary</h3>
        </div>
        <span className="result-status">Completed</span>
      </div>

      {scalarEntries.length > 0 && (
        <div className="result-summary-grid">
          {scalarEntries.map(([key, value]) => (
            <article className="result-summary-card" key={key}>
              <span className="result-label">{formatLabel(key)}</span>
              <strong>{formatValue(key, value)}</strong>
            </article>
          ))}
        </div>
      )}

      {complexEntries.map(([key, value]) => (
        <section className="result-section" key={key}>
          <h4>{formatLabel(key)}</h4>
          <ResultValue label={key} value={value} />
        </section>
      ))}

      <details className="result-raw-details">
        <summary>View raw API response</summary>
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </details>
    </div>
  );
}

type ToolPage = "overview" | "valuation" | "quality" | "model-monitor" | "pricing" | "projection" | "reports";

export default function ActuarialTools({ activePage }: { activePage: ToolPage }) {
  const [baseline, setBaseline] = useState(
    '{"reserve": 100000, "profit": 12000}',
  );
  const [candidate, setCandidate] = useState(
    '{"reserve": 108000, "profit": 10500}',
  );
  const [threshold, setThreshold] = useState("5");
  const [sumAssured, setSumAssured] = useState("500000");
  const [probability, setProbability] = useState("0.02");
  const [expense, setExpense] = useState("10");
  const [risk, setRisk] = useState("5");
  const [start, setStart] = useState("1000000");
  const [growth, setGrowth] = useState("4");
  const [years, setYears] = useState("10");
  const [result, setResult] = useState<AnyResult | null>(null);
  const [resultPage, setResultPage] = useState<ToolPage | null>(null);
  const [error, setError] = useState("");
  const [errorPage, setErrorPage] = useState<ToolPage | null>(null);
  const [loading, setLoading] = useState(false);

  async function callTool(
    path: string,
    body: Record<string, unknown>,
  ) {
    setLoading(true);
    setError("");
    setErrorPage(null);
    setResult(null);
    setResultPage(null);
    const requestedPage = activePage;

    try {
      const response = await fetch(`${API_URL}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const payload: unknown = await response.json();

      if (!response.ok) {
        const detail =
          payload !== null &&
            typeof payload === "object" &&
            "detail" in payload &&
            typeof payload.detail === "string"
            ? payload.detail
            : "The calculation could not be completed.";

        throw new Error(detail);
      }

      if (
        payload === null ||
        typeof payload !== "object" ||
        Array.isArray(payload)
      ) {
        throw new Error("The API returned an unexpected response.");
      }

      setResult(payload as AnyResult);
      setResultPage(requestedPage);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not connect to the ActuTrace API. Check that the backend is running.",
      );
      setErrorPage(requestedPage);
    } finally {
      setLoading(false);
    }
  }

  function parseModelOutputs() {
    setError("");
    setErrorPage(null);

    try {
      const baselineData: unknown = JSON.parse(baseline);
      const candidateData: unknown = JSON.parse(candidate);
      const thresholdValue = Number(threshold);

      if (
        baselineData === null ||
        typeof baselineData !== "object" ||
        Array.isArray(baselineData) ||
        candidateData === null ||
        typeof candidateData !== "object" ||
        Array.isArray(candidateData)
      ) {
        throw new Error(
          "Baseline and candidate must both be JSON objects.",
        );
      }

      if (
        !Number.isFinite(thresholdValue) ||
        thresholdValue < 0 ||
        thresholdValue > 100
      ) {
        throw new Error("Threshold must be between 0 and 100.");
      }

      void callTool("/tools/model-monitor", {
        baseline: baselineData,
        candidate: candidateData,
        materiality_percent: thresholdValue,
      });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Enter valid JSON objects for both model outputs.",
      );
      setErrorPage("model-monitor");
    }
  }

  return (
    <section className="panel actuarial-tools" hidden={!(["model-monitor", "pricing", "projection", "reports"] as ToolPage[]).includes(activePage)}>
      <p className="eyebrow">ACTUARIAL WORKBENCH · EXPERIMENTAL</p>
      <h2>Additional actuarial tools</h2>
      <p className="panel-description">
        Explore model changes, pricing assumptions, and multi-year growth
        scenarios. These are educational calculations, not production
        actuarial models.
      </p>

      <div className="tool-grid">
        <article className="tool-card" id="model-monitor-section" hidden={activePage !== "model-monitor"}>
          <h3>1. Model Change Monitor</h3>
          <p>Compare named output metrics from two model runs.</p>

          <label>
            Baseline outputs (JSON)
            <textarea
              rows={3}
              value={baseline}
              onChange={(e) => setBaseline(e.target.value)}
            />
          </label>

          <label>
            Candidate outputs (JSON)
            <textarea
              rows={3}
              value={candidate}
              onChange={(e) => setCandidate(e.target.value)}
            />
          </label>

          <label>
            Flag change threshold (%)
            <input
              type="number"
              min="0"
              max="100"
              value={threshold}
              onChange={(e) => setThreshold(e.target.value)}
            />
          </label>

          <button disabled={loading} onClick={parseModelOutputs}>
            Compare outputs
          </button>
        </article>

        <article className="tool-card" id="pricing-section" hidden={activePage !== "pricing"}>
          <h3>2. Pricing Scenario Simulator</h3>
          <p>
            Estimate expected claim cost plus configurable expense and risk
            loads.
          </p>

          <label>
            Sum assured (₹)
            <input
              type="number"
              min="0"
              value={sumAssured}
              onChange={(e) => setSumAssured(e.target.value)}
            />
          </label>

          <label>
            Claim probability (0–1)
            <input
              type="number"
              min="0"
              max="1"
              step="0.001"
              value={probability}
              onChange={(e) => setProbability(e.target.value)}
            />
          </label>

          <label>
            Expense load (%)
            <input
              type="number"
              min="0"
              max="500"
              value={expense}
              onChange={(e) => setExpense(e.target.value)}
            />
          </label>

          <label>
            Risk load (%)
            <input
              type="number"
              min="0"
              max="500"
              value={risk}
              onChange={(e) => setRisk(e.target.value)}
            />
          </label>

          <button
            disabled={loading}
            onClick={() =>
              void callTool("/tools/pricing-simulator", {
                sum_assured: Number(sumAssured),
                claim_probability: Number(probability),
                expense_load_percent: Number(expense),
                risk_load_percent: Number(risk),
              })
            }
          >
            Calculate scenario
          </button>
        </article>

        <article className="tool-card" id="projection-section" hidden={activePage !== "projection"}>
          <h3>3. Liability Growth Projection</h3>
          <p>
            Project an amount using a constant annual growth assumption.
          </p>

          <label>
            Starting amount (₹)
            <input
              type="number"
              min="0"
              value={start}
              onChange={(e) => setStart(e.target.value)}
            />
          </label>

          <label>
            Annual growth (%)
            <input
              type="number"
              min="-100"
              max="100"
              step="0.1"
              value={growth}
              onChange={(e) => setGrowth(e.target.value)}
            />
          </label>

          <label>
            Years (1–100)
            <input
              type="number"
              min="1"
              max="100"
              value={years}
              onChange={(e) => setYears(e.target.value)}
            />
          </label>

          <button
            disabled={loading}
            onClick={() =>
              void callTool("/tools/liability-projection", {
                starting_amount: Number(start),
                annual_growth_percent: Number(growth),
                years: Number(years),
              })
            }
          >
            Project scenario
          </button>
        </article>

        <article className="tool-card" id="reports-section" hidden={activePage !== "reports"}>
          <h3>4. Audit &amp; Reporting</h3>
          <p>
            Download the latest run metadata, input hashes, configuration,
            and current reports.
          </p>

          <a
            className="tool-link"
            href={`${API_URL}/reports/analysis_summary.json`}
          >
            Analysis audit summary (JSON) ↓
          </a>
          <a
            className="tool-link"
            href={`${API_URL}/reports/validation_findings.csv`}
          >
            Validation findings (CSV) ↓
          </a>
          <a
            className="tool-link"
            href={`${API_URL}/reports/valuation_impacts.csv`}
          >
            Valuation impacts (CSV) ↓
          </a>
        </article>
      </div>

      {loading && (
        <p role="status" className="tool-loading">
          <span className="loading-dot" />
          Calculating scenario…
        </p>
      )}

      {error && errorPage === activePage && (
        <div className="tool-error" role="alert">
          <strong>Unable to complete the request</strong>
          <p>{error}</p>
        </div>
      )}

      {result && resultPage === activePage && <ResultDisplay result={result} />}

      <p className="helper-text">
        Pricing and liability outputs are deterministic illustrations, not
        approved premiums, reserves, regulatory valuations, or financial
        advice.
      </p>
    </section>
  );
}
