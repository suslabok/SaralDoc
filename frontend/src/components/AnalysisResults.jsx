export default function AnalysisResults({ data }) {
  if (!data) return null;

  return (
    <div className="results-box">
      <h2>Analysis Results</h2>

      <div className="result-section">
        <h3>📊 Document Summary</h3>
        <ul>
          <li>
            <strong>Text Length:</strong> {data.text_length} characters
          </li>
          <li>
            <strong>Number of Clauses:</strong> {data.num_clauses}
          </li>
        </ul>
      </div>

      {data.clauses && data.clauses.length > 0 && (
        <div className="result-section">
          <h3>📝 Extracted Clauses</h3>
          <div className="clauses-list">
            {data.clauses.map((clause, idx) => (
              <div key={idx} className="clause-item">
                <p>{clause}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.obligations && data.obligations.length > 0 && (
        <div className="result-section">
          <h3>⚖️ Obligations & Duties</h3>
          <div className="obligations-list">
            {data.obligations.map((obligation, idx) => (
              <div key={idx} className="obligation-item">
                <strong>Type:</strong> {obligation.type}
                <p>{obligation.clause}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {(!data.obligations || data.obligations.length === 0) && (
        <div className="result-section">
          <p className="note">
            No obligations detected. Refine your document or check the backend
            extraction rules.
          </p>
        </div>
      )}
    </div>
  );
}
