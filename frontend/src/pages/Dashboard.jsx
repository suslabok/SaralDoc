import { useState, useRef, useEffect } from "react";

// ── All styles inlined ────────────────────────────────────────────────────────
const css = `
  @import url('https://fonts.googleapis.com/css2?family=Hind:wght@400;500;600;700&family=Lora:ital,wght@0,500;0,600;1,400&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  @keyframes fadeIn    { from { opacity:0; transform:translateY(10px);  } to { opacity:1; transform:translateY(0); } }
  @keyframes slideInUp { from { opacity:0; transform:translateY(20px);  } to { opacity:1; transform:translateY(0); } }
  @keyframes slideInDn { from { opacity:0; transform:translateY(-10px); } to { opacity:1; transform:translateY(0); } }
  @keyframes float     { 0%,100%{ transform:translateY(0); } 50%{ transform:translateY(-8px); } }
  @keyframes spin      { to { transform:rotate(360deg); } }
  @keyframes barGrow   { from { width:0; } }

  /* ── Root ── */
  .sd-root {
    min-height: 100vh;
    background: var(--bg-primary);
    font-family: var(--font-body);
    animation: fadeIn 0.3s ease-out;
  }

  /* ── Page body ── */
  .sd-body {
    padding: 48px 40px 40px;
    max-width: 1400px;
    margin: 0 auto;
  }

  /* ── Stats row ── */
  .sd-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
  }
  .sd-stat {
    background: white;
    padding: 26px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
    animation: slideInUp 0.4s ease-out;
  }
  .sd-stat::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--primary);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.2s ease;
  }
  .sd-stat:hover { transform: translateY(-4px); box-shadow: var(--shadow); border-color: var(--primary); }
  .sd-stat:hover::before { transform: scaleX(1); }
  .sd-stat-icon { font-size: 2.2em; margin-bottom: 10px; display: block; }
  .sd-stat-num  { font-family: var(--font-heading); font-size: 2em; font-weight: 600; color: var(--primary); }
  .sd-stat-lbl  { color: var(--text-secondary); font-size: 0.88em; font-weight: 500; margin-top: 4px; }

  /* ── Main grid ── */
  .sd-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 28px;
  }
  @media (max-width: 1024px) { .sd-grid { grid-template-columns: 1fr; } }

  /* ── Cards ── */
  .sd-card {
    background: white;
    padding: 34px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    animation: slideInUp 0.4s ease-out;
  }
  .sd-card-title {
    font-family: var(--font-heading);
    font-size: 1.2em;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 14px;
    margin-bottom: 22px;
    border-bottom: 2px solid var(--primary);
  }

  /* ── Tabs ── */
  .sd-tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 22px; }
  .sd-tab {
    padding: 9px 16px;
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-secondary);
    font-family: var(--font-body);
    font-weight: 500;
    cursor: pointer;
    border-radius: var(--radius-sm, 6px);
    transition: all 0.2s ease;
    font-size: 0.92em;
  }
  .sd-tab:hover { border-color: var(--primary); color: var(--primary); }
  .sd-tab.active {
    background: var(--primary);
    color: #faf8f3;
    border-color: var(--primary);
  }

  /* ── Error alert ── */
  .sd-error {
    display: flex; align-items: flex-start; gap: 10px;
    background: rgba(168,73,46,0.08); border: 1px solid rgba(168,73,46,0.25);
    border-radius: 8px; padding: 14px;
    margin-bottom: 18px;
    animation: slideInDn 0.3s ease-out;
  }
  .sd-error p { color: var(--primary); margin: 0; flex: 1; font-size: 0.93em; }
  .sd-error button { background: none; border: none; color: var(--primary); font-size: 1.2em; cursor: pointer; }

  /* ── Upload zone ── */
  .sd-upload {
    border: 2px dashed var(--border);
    border-radius: 10px;
    padding: 50px 30px;
    text-align: center;
    background: var(--bg-primary);
    transition: all 0.2s ease;
    margin-bottom: 22px;
    cursor: pointer;
  }
  .sd-upload.drag-over {
    border-color: var(--primary);
    background: rgba(168,73,46,0.05);
    box-shadow: var(--shadow);
  }
  .sd-upload-icon { font-size: 3em; display: block; margin-bottom: 12px; animation: float 3s ease-in-out infinite; }
  .sd-upload h3 { font-size: 1.15em; color: var(--text-primary); margin-bottom: 6px; font-family: var(--font-heading); font-weight: 600; }
  .sd-upload p  { color: var(--text-secondary); font-size: 0.9em; margin: 4px 0; }
  .sd-upload-hint { font-size: 0.85em; color: var(--text-secondary); opacity: 0.8; }

  .sd-browse {
    margin-top: 16px; padding: 10px 26px;
    background: var(--primary);
    color: #faf8f3; border: none; border-radius: var(--radius-sm, 6px);
    font-weight: 600; cursor: pointer;
    font-family: var(--font-body);
    transition: all 0.2s ease;
  }
  .sd-browse:hover { background: var(--primary-hover); }

  .sd-file-chip {
    display: flex; align-items: center; justify-content: space-between;
    margin-top: 14px; padding: 10px 14px;
    background: rgba(168,73,46,0.08); border-radius: var(--radius-sm, 6px);
    color: var(--primary); font-weight: 600; font-size: 0.9em;
  }
  .sd-file-chip button { background: none; border: none; color: var(--primary); cursor: pointer; font-size: 1.1em; }

  /* ── Textarea ── */
  .sd-textarea {
    width: 100%; min-height: 280px;
    padding: 18px; border: 1px solid var(--border);
    border-radius: 8px; font-family: var(--font-body, monospace);
    font-size: 0.94em; resize: vertical; line-height: 1.65;
    transition: all 0.2s ease; margin-bottom: 22px;
    color: var(--text-primary);
  }
  .sd-textarea:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(168,73,46,0.1); }
  .sd-textarea::placeholder { color: var(--text-secondary); opacity: 0.6; }

  /* ── Action buttons ── */
  .sd-actions { display: flex; gap: 14px; }
  .sd-btn-primary, .sd-btn-secondary {
    flex: 1; padding: 13px 20px; border: none;
    border-radius: var(--radius-sm, 6px); font-weight: 600;
    font-size: 0.95em; cursor: pointer;
    font-family: var(--font-body);
    transition: all 0.2s ease;
  }
  .sd-btn-primary { background: var(--primary); color: #faf8f3; }
  .sd-btn-primary:hover:not(:disabled)   { background: var(--primary-hover); }
  .sd-btn-secondary { background: white; border: 1px solid var(--primary); color: var(--primary); }
  .sd-btn-secondary:hover:not(:disabled) { background: var(--primary); color: #faf8f3; }
  .sd-btn-primary:disabled, .sd-btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }

  /* ── Empty state ── */
  .sd-empty { text-align: center; padding: 60px 20px; color: var(--text-secondary); }
  .sd-empty-icon { font-size: 3.5em; display: block; margin-bottom: 16px; opacity: 0.7; }
  .sd-empty strong { display: block; font-size: 1.1em; color: var(--text-primary); margin-bottom: 6px; font-family: var(--font-heading); }

  /* ── Loading spinner ── */
  .sd-loading { text-align: center; padding: 50px 20px; }
  .sd-spinner {
    width: 40px; height: 40px; margin: 0 auto 16px;
    border: 3px solid rgba(168,73,46,0.15);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 0.75s linear infinite;
  }
  .sd-loading p { color: var(--text-secondary); font-weight: 500; }

  /* ── Result items ── */
  .sd-results {
    animation: fadeIn 0.3s ease-out;
    display: flex; flex-direction: column; gap: 12px;
    max-height: 480px; overflow-y: auto; padding-right: 4px;
  }
  .sd-results::-webkit-scrollbar { width: 5px; }
  .sd-results::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

  .sd-result-item {
    background: var(--bg-primary);
    padding: 16px; border-left: 4px solid var(--primary);
    border-radius: 8px; transition: all 0.2s ease;
  }
  .sd-result-item:hover { transform: translateX(3px); }
  .sd-result-item.obligation { border-left-color: var(--amber, #c08a34); background: rgba(192,138,52,0.06); }

  .sd-item-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
  .sd-badge {
    padding: 3px 10px; border-radius: 6px;
    font-size: 0.82em; font-weight: 600;
    background: var(--primary);
    color: #faf8f3;
  }
  .sd-badge.obl  { background: var(--amber, #c08a34); }
  .sd-badge.conf { background: rgba(168,73,46,0.1); color: var(--primary); }
  .sd-item-text  { color: var(--text-primary); line-height: 1.65; font-size: 0.95em; }
  .sd-item-meta  { color: var(--text-secondary); font-size: 0.83em; margin-top: 6px; }

  /* ── Entities ── */
  .sd-entity {
    display: flex; align-items: center; gap: 12px;
    padding: 11px 14px; background: var(--bg-primary);
    border-radius: 8px; border: 1px solid var(--border);
    transition: all 0.2s ease;
  }
  .sd-entity:hover { border-color: var(--primary); }
  .sd-entity-badge {
    background: var(--secondary);
    color: #faf8f3; padding: 3px 12px; border-radius: 999px;
    font-size: 0.78em; font-weight: 600; white-space: nowrap;
  }
  .sd-entity-text { flex: 1; color: var(--text-primary); font-weight: 500; font-size: 0.94em; }
  .sd-entity-conf { color: var(--primary); font-weight: 600; font-size: 0.88em; }

  /* ── Summary ── */
  .sd-summary { display: flex; flex-direction: column; gap: 18px; }
  .sd-summary-card {
    background: var(--bg-primary);
    padding: 22px; border-radius: 8px;
    border-left: 4px solid var(--primary);
  }
  .sd-summary-card h4 { color: var(--text-primary); margin-bottom: 14px; font-family: var(--font-heading); font-size: 1.05em; font-weight: 600; }
  .sd-summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 14px; }
  .sd-summary-item { display: flex; flex-direction: column; gap: 5px; }
  .sd-summary-item .lbl { color: var(--text-secondary); font-size: 0.87em; font-weight: 500; }
  .sd-summary-item .val { color: var(--primary); font-family: var(--font-heading); font-size: 1.4em; font-weight: 600; }
  .sd-score-bar-bg { height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; margin-top: 6px; }
  .sd-score-bar    { height: 100%; border-radius: 4px; background: var(--primary); animation: barGrow 0.8s ease-out; }
  .sd-summary-text { background: white; border: 1px solid var(--border); border-radius: 8px; padding: 16px; color: var(--text-primary); line-height: 1.7; font-size: 0.95em; }

  .sd-no-results { text-align: center; padding: 30px 20px; color: var(--text-secondary); font-size: 0.93em; }

  /* ── Responsive ── */
  @media (max-width: 768px) {
    .sd-body     { padding: 24px 20px; }
    .sd-card     { padding: 24px; }
    .sd-actions  { flex-direction: column; }
    .sd-summary-grid { grid-template-columns: 1fr; }
  }
`;

// ── Sub-components ─────────────────────────────────────────────────────────────

function StatCard({ icon, value, label }) {
  return (
    <div className="sd-stat">
      <span className="sd-stat-icon">{icon}</span>
      <div className="sd-stat-num">{value}</div>
      <div className="sd-stat-lbl">{label}</div>
    </div>
  );
}

function ResultItem({ item, index }) {
  return (
    <div className="sd-result-item">
      <div className="sd-item-head">
        <span className="sd-badge">#{index + 1}</span>
        {item.confidence != null && (
          <span className="sd-badge conf">
            {Math.round(item.confidence * 100)}%
          </span>
        )}
      </div>
      <div className="sd-item-text">
        {item.clause || item.text || JSON.stringify(item)}
      </div>
      {item.category && (
        <div className="sd-item-meta">Category: {item.category}</div>
      )}
    </div>
  );
}

function ObligationItem({ item, index }) {
  return (
    <div className="sd-result-item obligation">
      <div className="sd-item-head">
        <span className="sd-badge obl">
          {item.type || `Obligation ${index + 1}`}
        </span>
        {item.confidence != null && (
          <span className="sd-badge conf">
            {Math.round(item.confidence * 100)}%
          </span>
        )}
      </div>
      <div className="sd-item-text">
        {item.obligation || item.text || JSON.stringify(item)}
      </div>
      {item.language && (
        <div className="sd-item-meta">Language: {item.language}</div>
      )}
    </div>
  );
}

function EntityItem({ item }) {
  return (
    <div className="sd-entity">
      <span className="sd-entity-badge">{item.type || "ENTITY"}</span>
      <span className="sd-entity-text">{item.text || item.entity}</span>
      {item.confidence != null && (
        <span className="sd-entity-conf">
          {Math.round(item.confidence * 100)}%
        </span>
      )}
    </div>
  );
}

function SummaryPanel({ results }) {
  const score = results.complexity_score ?? null;
  const read = results.readability_score ?? null;

  return (
    <div className="sd-summary">
      <div className="sd-summary-card">
        <h4>📊 Document Metrics</h4>
        <div className="sd-summary-grid">
          {results.language && (
            <div className="sd-summary-item">
              <span className="lbl">Language</span>
              <span className="val" style={{ fontSize: "1em", paddingTop: 4 }}>
                {results.language}
              </span>
            </div>
          )}
          {score != null && (
            <div className="sd-summary-item">
              <span className="lbl">Complexity</span>
              <span className="val">{score}</span>
              <div className="sd-score-bar-bg">
                <div className="sd-score-bar" style={{ width: `${score}%` }} />
              </div>
            </div>
          )}
          {read != null && (
            <div className="sd-summary-item">
              <span className="lbl">Readability</span>
              <span className="val">{read}</span>
              <div className="sd-score-bar-bg">
                <div
                  className="sd-score-bar"
                  style={{
                    width: `${read}%`,
                    background:
                      "linear-gradient(90deg, var(--risk-low), var(--secondary))",
                  }}
                />
              </div>
            </div>
          )}
          {results.total_clauses != null && (
            <div className="sd-summary-item">
              <span className="lbl">Total Clauses</span>
              <span className="val">{results.total_clauses}</span>
            </div>
          )}
        </div>
      </div>
      {results.summary && (
        <div>
          <div
            className="sd-badge"
            style={{ marginBottom: 8, display: "inline-block" }}
          >
            Summary
          </div>
          <div className="sd-summary-text">{results.summary}</div>
        </div>
      )}
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────

const VALID_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/msword",
  "text/plain",
];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
const API = "http://localhost:8000";

export default function SaralDoc() {
  const [inputMethod, setInputMethod] = useState("upload");
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("clauses");

  const fileRef = useRef(null);

  // Inject styles once
  useEffect(() => {
    const id = "saraldoc-styles";
    if (!document.getElementById(id)) {
      const tag = document.createElement("style");
      tag.id = id;
      tag.textContent = css;
      document.head.appendChild(tag);
    }
  }, []);

  // ── File validation ──────────────────────────────────────────────────────────
  const validateAndSetFile = (f) => {
    if (!f) return;
    if (!VALID_TYPES.includes(f.type)) {
      setError("Only PDF, DOCX, and TXT files are supported.");
      return;
    }
    if (f.size > MAX_FILE_SIZE) {
      setError("File size must be less than 10 MB.");
      return;
    }
    setFile(f);
    setError(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    validateAndSetFile(e.dataTransfer.files[0]);
  };

  // ── Analyze ──────────────────────────────────────────────────────────────────
  const analyze = async () => {
    if (inputMethod === "upload" && !file) {
      setError("Please select a file first.");
      return;
    }
    if (inputMethod === "paste" && !text.trim()) {
      setError("Please paste document text first.");
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      let res;
      if (inputMethod === "paste") {
        res = await fetch(`${API}/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text,
            language: "auto",
            extract_summary: true,
          }),
        });
      } else {
        const form = new FormData();
        form.append("file", file);
        res = await fetch(`${API}/analyze-file`, {
          method: "POST",
          body: form,
        });
      }

      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      if (data.success === false)
        throw new Error(data.error || "Analysis failed.");
      setResults(data);
      setActiveTab("clauses");
    } catch (e) {
      setError(`${e.message}. Make sure the backend is running.`);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setText("");
    setResults(null);
    setError(null);
    if (fileRef.current) fileRef.current.value = "";
  };

  // ── Tabs with data ────────────────────────────────────────────────────────────
  const resultTabs = results
    ? ["clauses", "obligations", "entities", "summary"].filter(
        (t) => t === "summary" || results[t]?.length > 0,
      )
    : [];

  const TAB_LABELS = {
    clauses: `📜 Clauses (${results?.clauses?.length ?? 0})`,
    obligations: `⚖️ Obligations (${results?.obligations?.length ?? 0})`,
    entities: `🏷️ Entities (${results?.entities?.length ?? 0})`,
    summary: "📊 Summary",
  };

  return (
    <div className="sd-root">
      <div className="sd-body">
        {/* ── Stats row ── */}
        <div className="sd-stats">
          <StatCard
            icon="📄"
            value={results?.total_clauses ?? "—"}
            label="Clauses Found"
          />
          <StatCard
            icon="⚖️"
            value={results?.obligations?.length ?? "—"}
            label="Obligations"
          />
          <StatCard
            icon="🏷️"
            value={results?.entities?.length ?? "—"}
            label="Entities"
          />
          <StatCard
            icon="📊"
            value={
              results?.complexity_score != null ? results.complexity_score : "—"
            }
            label="Complexity Score"
          />
        </div>

        {/* ── Main grid ── */}
        <div className="sd-grid">
          {/* ── INPUT CARD ── */}
          <div className="sd-card">
            <div className="sd-card-title">📋 Analyze Document</div>

            {/* Method tabs */}
            <div className="sd-tabs">
              <button
                className={`sd-tab ${inputMethod === "upload" ? "active" : ""}`}
                onClick={() => {
                  setInputMethod("upload");
                  setText("");
                }}
              >
                📂 Upload File
              </button>
              <button
                className={`sd-tab ${inputMethod === "paste" ? "active" : ""}`}
                onClick={() => {
                  setInputMethod("paste");
                  setFile(null);
                }}
              >
                ✍️ Paste Text
              </button>
            </div>

            {/* Error */}
            {error && (
              <div className="sd-error">
                <span>⚠️</span>
                <p>{error}</p>
                <button onClick={() => setError(null)}>✕</button>
              </div>
            )}

            {/* Upload zone */}
            {inputMethod === "upload" && (
              <div
                className={`sd-upload ${dragOver ? "drag-over" : ""}`}
                onClick={() => fileRef.current?.click()}
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragOver(true);
                }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
              >
                <span className="sd-upload-icon">📁</span>
                <h3>Drag &amp; drop your file here</h3>
                <p>or click to browse</p>
                <p className="sd-upload-hint">
                  Supported: PDF, DOCX, TXT · max 10 MB
                </p>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".pdf,.doc,.docx,.txt"
                  style={{ display: "none" }}
                  disabled={loading}
                  onChange={(e) => validateAndSetFile(e.target.files?.[0])}
                />
                <button
                  className="sd-browse"
                  onClick={(e) => {
                    e.stopPropagation();
                    fileRef.current?.click();
                  }}
                >
                  Browse Files
                </button>
                {file && (
                  <div
                    className="sd-file-chip"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <span>📎 {file.name}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setFile(null);
                        if (fileRef.current) fileRef.current.value = "";
                      }}
                    >
                      ✕
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Paste zone */}
            {inputMethod === "paste" && (
              <textarea
                className="sd-textarea"
                placeholder="Paste your Nepali or English legal document here…"
                value={text}
                disabled={loading}
                onChange={(e) => {
                  setText(e.target.value);
                  setError(null);
                }}
              />
            )}

            {/* Actions */}
            <div className="sd-actions">
              <button
                className="sd-btn-primary"
                onClick={analyze}
                disabled={
                  loading || (inputMethod === "paste" ? !text.trim() : !file)
                }
              >
                {loading ? "⏳ Analyzing…" : "🚀 Analyze Document"}
              </button>
              <button
                className="sd-btn-secondary"
                onClick={reset}
                disabled={loading}
              >
                ↺ Reset
              </button>
            </div>
          </div>

          {/* ── RESULTS CARD ── */}
          <div className="sd-card">
            <div className="sd-card-title">📈 Results</div>

            {/* Empty */}
            {!loading && !results && (
              <div className="sd-empty">
                <span className="sd-empty-icon">📋</span>
                <strong>No analysis yet</strong>
                Upload or paste a document and click Analyze to see results
                here.
              </div>
            )}

            {/* Spinner */}
            {loading && (
              <div className="sd-loading">
                <div className="sd-spinner" />
                <p>Analyzing your document…</p>
              </div>
            )}

            {/* Results */}
            {!loading && results && (
              <>
                <div className="sd-tabs">
                  {resultTabs.map((t) => (
                    <button
                      key={t}
                      className={`sd-tab ${activeTab === t ? "active" : ""}`}
                      onClick={() => setActiveTab(t)}
                    >
                      {TAB_LABELS[t]}
                    </button>
                  ))}
                </div>

                <div className="sd-results">
                  {activeTab === "clauses" &&
                    (results.clauses?.length ? (
                      results.clauses.map((c, i) => (
                        <ResultItem key={i} item={c} index={i} />
                      ))
                    ) : (
                      <div className="sd-no-results">No clauses found.</div>
                    ))}

                  {activeTab === "obligations" &&
                    (results.obligations?.length ? (
                      results.obligations.map((o, i) => (
                        <ObligationItem key={i} item={o} index={i} />
                      ))
                    ) : (
                      <div className="sd-no-results">No obligations found.</div>
                    ))}

                  {activeTab === "entities" &&
                    (results.entities?.length ? (
                      results.entities.map((e, i) => (
                        <EntityItem key={i} item={e} />
                      ))
                    ) : (
                      <div className="sd-no-results">No entities found.</div>
                    ))}

                  {activeTab === "summary" && (
                    <SummaryPanel results={results} />
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
