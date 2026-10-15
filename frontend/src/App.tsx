
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

type Finding = {
  row_number: string;
  policy_id: string;
  field: string;
  severity: string;
  message: string;
};

type Impact = {
  rank: string;
  defect_id: string;
  policy_id: string;
  original_value: string;
  altered_value: string;
  impact: string;
  is_material: string;
};

type Analysis = {
  validation: {
    finding_count: number;
    severity_counts: Record<string, number>;
  };
  valuation: {
    baseline_expected_cost: number;
    defect_count: number;
    material_defect_count: number;
    combined_impact: number;
    interaction_residual: number;
    materiality_threshold_percent: number;
    valuation_basis: string;
  };
  validation_findings: Finding[];
  valuation_impacts: Impact[];
};

function money(value: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}


type PriorityComparison = {
  defect_type_count: number;
  spearman_rank_correlation: number | null;
  ranking_differs: boolean;
  data_basis: string;
  results: {
    defect_type: string;
    occurrence_count: number;
    total_absolute_impact: number;
    count_rank: number;
    impact_rank: number;
  }[];
  interpretation: string;
};

function App() {
  const [data, setData] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [comparison, setComparison] = useState<PriorityComparison | null>(null);


  async function runAnalysis() {
    setLoading(true);
    setError("");

    try {
      // Run the main policy validation and valuation analysis.
      const response = await fetch(`${API_URL}/analysis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          claim_probability: 0.02,
          materiality_threshold_percent: 5,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof result.detail === "string"
            ? result.detail
            : "The analysis failed. Check the backend terminal.",
        );
      }

      setData(result);

      // Fetch the separate count-versus-impact comparison.
      const comparisonResponse = await fetch(
        `${API_URL}/priority-comparison`,
      );

      if (!comparisonResponse.ok) {
        throw new Error("Priority comparison could not be loaded.");
      }

      const comparisonResult: PriorityComparison =
        await comparisonResponse.json();

      setComparison(comparisonResult);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Unable to connect to the ActuTrace API.",
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="dashboard">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-icon">A</span>
          ActuTrace
        </a>
        <span className="environment">
          <span className="online-dot" />
          Local analysis environment
        </span>
      </header>

      <section className="hero">
        <p className="eyebrow">ACTUARIAL DATA QUALITY PLATFORM</p>
        <h1>Know which data defects matter financially.</h1>
        <p className="hero-description">
          Validate life-insurance policy records, measure simulated
          valuation impacts, and prioritize defects by estimated impact.
        </p>
        <button
          className="primary-button"
          onClick={runAnalysis}
          disabled={loading}
        >
          {loading ? "Analysing..." : "Run analysis →"}
        </button>
        <p className="helper-text">
          Demonstration using synthetic policy data.
        </p>
      </section>

      {error && (
        <div className="error-box" role="alert">
          <strong>Analysis could not be completed</strong>
          <p>{error}</p>
          <p>
            Check that the FastAPI backend is running at
            {" "}http://127.0.0.1:8000.
          </p>
        </div>
      )}

      {!data && !error && (
        <section className="empty-state">
          <div className="empty-icon">↗</div>
          <h2>Your analysis workspace</h2>
          <p>
            Run an analysis to view validation findings, impact rankings,
            and report downloads.
          </p>
        </section>
      )}

      {data && (
        <>
          <section className="section-heading">
            <div>
              <p className="eyebrow">RESULTS OVERVIEW</p>
              <h2>Portfolio analysis</h2>
            </div>
            <span className="complete-badge">Analysis complete</span>
          </section>

          <section className="metric-grid">
            <article className="metric-card">
              <p>Validation findings</p>
              <strong>{data.validation.finding_count}</strong>
              <span>
                {data.validation.severity_counts.high ?? 0} high severity
              </span>
            </article>
            <article className="metric-card">
              <p>Simulated defects</p>
              <strong>{data.valuation.defect_count}</strong>
              <span>Controlled experiment</span>
            </article>
            <article className="metric-card">
              <p>Material defects</p>
              <strong>{data.valuation.material_defect_count}</strong>
              <span>
                Threshold: {data.valuation.materiality_threshold_percent}%
              </span>
            </article>
            <article className="metric-card">
              <p>Baseline expected cost</p>
              <strong>{money(data.valuation.baseline_expected_cost)}</strong>
              <span>Before simulated defects</span>
            </article>
          </section>

          <section className="panel">
            <p className="eyebrow">FINANCIAL PRIORITIZATION</p>
            <h2>Valuation impact ranking</h2>
            <p className="panel-description">
              Each injected defect is measured against the clean synthetic
              baseline. This simplified model is for demonstration, not
              production actuarial valuation.
            </p>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Defect</th>
                    <th>Policy</th>
                    <th>Change in sum assured</th>
                    <th>Estimated impact</th>
                    <th>Materiality</th>
                  </tr>
                </thead>
                <tbody>
                  {data.valuation_impacts.map((item) => (
                    <tr key={item.defect_id}>
                      <td>#{item.rank}</td>
                      <td>{item.defect_id}</td>
                      <td>{item.policy_id}</td>
                      <td>
                        {money(
                          Number(item.altered_value) -
                          Number(item.original_value),
                        )}
                      </td>
                      <td className="impact-value">
                        {money(Number(item.impact))}
                      </td>
                      <td>
                        <span
                          className={
                            item.is_material === "True"
                              ? "pill material"
                              : "pill non-material"
                          }
                        >
                          {item.is_material === "True"
                            ? "Material"
                            : "Below threshold"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          {comparison && (
            <section className="panel">
              <p className="eyebrow">ACTUTRACE DIFFERENTIATOR</p>
              <h2>Count vs financial-impact priority</h2>

              <p className="panel-description">
                Compare defect frequency with the total absolute estimated
                impact for each category in a controlled synthetic example.
              </p>

              <div className="comparison-summary">
                <div>
                  <span>Spearman rank correlation</span>
                  <strong>
                    {comparison.spearman_rank_correlation === null
                      ? "Not available"
                      : comparison.spearman_rank_correlation.toFixed(2)}
                  </strong>
                </div>

                <div>
                  <span>Do the rankings differ?</span>
                  <strong>{comparison.ranking_differs ? "Yes" : "No"}</strong>
                </div>
              </div>

              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Defect category</th>
                      <th>Occurrences</th>
                      <th>Count rank</th>
                      <th>Total absolute impact</th>
                      <th>Impact rank</th>
                    </tr>
                  </thead>

                  <tbody>
                    {comparison.results.map((item) => (
                      <tr key={item.defect_type}>
                        <td>{item.defect_type}</td>
                        <td>{item.occurrence_count}</td>
                        <td>#{item.count_rank}</td>
                        <td>{money(item.total_absolute_impact)}</td>
                        <td className="impact-value">
                          #{item.impact_rank}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <p className="panel-description">
                {comparison.interpretation}
              </p>

              <p className="helper-text">{comparison.data_basis}</p>
            </section>
          )}
          <section className="two-column">
            <article className="panel">
              <p className="eyebrow">PORTFOLIO CHANGE</p>
              <h2>Combined estimated impact</h2>
              <p className="large-number">
                {money(data.valuation.combined_impact)}
              </p>
              <p className="panel-description">
                Interaction residual:{" "}
                {money(data.valuation.interaction_residual)}
              </p>
            </article>

            <article className="panel">
              <p className="eyebrow">REPORT EXPORTS</p>
              <h2>Analysis reports</h2>
              <div className="download-list">
                <a href={`${API_URL}/reports/validation_findings.csv`}>
                  Validation findings <span>Download CSV ↓</span>
                </a>
                <a href={`${API_URL}/reports/valuation_impacts.csv`}>
                  Valuation impacts <span>Download CSV ↓</span>
                </a>
              </div>
            </article>
          </section>

          <section className="panel">
            <p className="eyebrow">DATA QUALITY</p>
            <h2>Validation findings</h2>
            <p className="panel-description">
              These findings describe detected data-quality issues. They do
              not automatically imply a measured valuation impact.
            </p>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Row</th>
                    <th>Policy</th>
                    <th>Field</th>
                    <th>Severity</th>
                    <th>Finding</th>
                  </tr>
                </thead>
                <tbody>
                  {data.validation_findings.map((finding, index) => (
                    <tr
                      key={`${finding.policy_id}-${finding.field}-${index}`}
                    >
                      <td>{finding.row_number}</td>
                      <td>{finding.policy_id || "—"}</td>
                      <td>{finding.field}</td>
                      <td>
                        <span
                          className={`pill ${finding.severity.toLowerCase()}`}
                        >
                          {finding.severity}
                        </span>
                      </td>
                      <td>{finding.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <p className="disclaimer">
            ActuTrace uses synthetic data and a simplified expected-claim-cost
            model. Its results are illustrative, not production reserve
            estimates or financial advice.
          </p>
        </>
      )}
    </main>
  );
}

export default App;
