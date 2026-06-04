import { useState, useRef, useEffect } from "react";

// ── All styles inlined ────────────────────────────────────────────────────────
const css = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800;900&family=DM+Sans:wght@300;400;500;600&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --accent:      #667eea;
    --accent2:     #764ba2;
    --dark:        #1a1b2e;
    --muted:       #7f8c8d;
    --border:      #e0e6ed;
    --bg:          linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
    --card-shadow: 0 10px 40px rgba(0,0,0,0.08);
    --radius:      20px;
    --font-display:'Syne', sans-serif;
    --font-body:   'DM Sans', sans-serif;
  }

  body { font-family: var(--font-body); }

  @keyframes fadeIn    { from { opacity:0; transform:translateY(10px);  } to { opacity:1; transform:translateY(0); } }
  @keyframes slideInUp { from { opacity:0; transform:translateY(20px);  } to { opacity:1; transform:translateY(0); } }
  @keyframes slideInDn { from { opacity:0; transform:translateY(-10px); } to { opacity:1; transform:translateY(0); } }
  @keyframes float     { 0%,100%{ transform:translateY(0); } 50%{ transform:translateY(-12px); } }
  @keyframes spin      { to { transform:rotate(360deg); } }
  @keyframes barGrow   { from { width:0; } }

  /* ── Root ── */
  .sd-root {
    min-height: 100vh;
    background: var(--bg);
    font-family: var(--font-body);
    animation: fadeIn 0.3s ease-out;
  }

  /* ── Banner ── */
  .sd-banner {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
    padding: 48px 40px;
    text-align: center;
    color: white;
    box-shadow: 0 15px 40px rgba(102,126,234,0.3);
  }
  .sd-banner h1 {
    font-family: var(--font-display);
    font-size: 2.8em;
    font-weight: 900;
    letter-spacing: -0.5px;
    margin-bottom: 10px;
  }
  .sd-banner p { font-size: 1.1em; opacity: 0.92; font-weight: 500; }

  /* ── Page body ── */
  .sd-body {
    padding: 40px;
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
    padding: 28px;
    border-radius: var(--radius);
    box-shadow: var(--card-shadow);
    border: 2px solid transparent;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    animation: slideInUp 0.5s ease-out;
  }
  .sd-stat::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.3s ease;
  }
  .sd-stat:hover { transform: translateY(-6px); box-shadow: 0 15px 40px rgba(102,126,234,0.18); border-color: var(--accent); }
  .sd-stat:hover::before { transform: scaleX(1); }
  .sd-stat-icon { font-size: 2.4em; margin-bottom: 10px; display: block; }
  .sd-stat-num  { font-family: var(--font-display); font-size: 2.2em; font-weight: 800; color: var(--accent); }
  .sd-stat-lbl  { color: var(--muted); font-size: 0.9em; font-weight: 600; margin-top: 4px; }

  /* ── Main grid ── */
  .sd-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }
  @media (max-width: 1024px) { .sd-grid { grid-template-columns: 1fr; } }

  /* ── Cards ── */
  .sd-card {
    background: white;
    padding: 38px;
    border-radius: var(--radius);
    box-shadow: var(--card-shadow);
    border: 1px solid rgba(102,126,234,0.1);
    animation: slideInUp 0.5s ease-out;
  }
  .sd-card-title {
    font-family: var(--font-display);
    font-size: 1.25em;
    font-weight: 800;
    color: var(--dark);
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 14px;
    margin-bottom: 22px;
    border-bottom: 3px solid var(--accent);
  }

  /* ── Tabs ── */
  .sd-tabs { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 22px; }
  .sd-tab {
    padding: 10px 18px;
    background: transparent;
    border: 2px solid var(--border);
    color: var(--muted);
    font-family: var(--font-body);
    font-weight: 600;
    cursor: pointer;
    border-radius: 10px;
    transition: all 0.25s ease;
    font-size: 0.93em;
  }
  .sd-tab:hover { border-color: var(--accent); color: var(--accent); }
  .sd-tab.active {
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: white;
    border-color: transparent;
    box-shadow: 0 8px 20px rgba(102,126,234,0.28);
  }

  /* ── Error alert ── */
  .sd-error {
    display: flex; align-items: flex-start; gap: 10px;
    background: #fee; border: 2px solid #fcc;
    border-radius: 12px; padding: 14px;
    margin-bottom: 18px;
    animation: slideInDn 0.3s ease-out;
  }
  .sd-error p { color: #c33; margin: 0; flex: 1; font-size: 0.93em; }
  .sd-error button { background: none; border: none; color: #c33; font-size: 1.2em; cursor: pointer; }

  /* ── Upload zone ── */
  .sd-upload {
    border: 3px dashed var(--accent);
    border-radius: 16px;
    padding: 55px 30px;
    text-align: center;
    background: linear-gradient(135deg, rgba(102,126,234,0.05), rgba(118,75,162,0.03));
    transition: all 0.3s ease;
    margin-bottom: 22px;
    cursor: pointer;
  }
  .sd-upload.drag-over {
    border-color: var(--accent2);
    background: linear-gradient(135deg, rgba(102,126,234,0.13), rgba(118,75,162,0.08));
    transform: scale(1.02);
    box-shadow: 0 12px 36px rgba(102,126,234,0.18);
  }
  .sd-upload-icon { font-size: 3.2em; display: block; margin-bottom: 12px; animation: float 3s ease-in-out infinite; }
  .sd-upload h3 { font-size: 1.2em; color: var(--dark); margin-bottom: 6px; }
  .sd-upload p  { color: var(--muted); font-size: 0.9em; margin: 4px 0; }
  .sd-upload-hint { font-size: 0.85em; color: #aaa; }

  .sd-browse {
    margin-top: 16px; padding: 11px 28px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: white; border: none; border-radius: 10px;
    font-weight: 700; cursor: pointer;
    font-family: var(--font-body);
    transition: all 0.3s ease;
  }
  .sd-browse:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(102,126,234,0.3); }

  .sd-file-chip {
    display: flex; align-items: center; justify-content: space-between;
    margin-top: 14px; padding: 10px 14px;
    background: #e8f1ff; border-radius: 10px;
    color: var(--accent); font-weight: 600; font-size: 0.9em;
  }
  .sd-file-chip button { background: none; border: none; color: var(--accent); cursor: pointer; font-size: 1.1em; }

  /* ── Textarea ── */
  .sd-textarea {
    width: 100%; min-height: 280px;
    padding: 18px; border: 2px solid var(--border);
    border-radius: 12px; font-family: 'Courier New', monospace;
    font-size: 0.94em; resize: vertical; line-height: 1.65;
    transition: all 0.3s ease; margin-bottom: 22px;
    color: var(--dark);
  }
  .sd-textarea:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 20px rgba(102,126,234,0.15); }
  .sd-textarea::placeholder { color: #bbb; }

  /* ── Action buttons ── */
  .sd-actions { display: flex; gap: 14px; }
  .sd-btn-primary, .sd-btn-secondary {
    flex: 1; padding: 14px 20px; border: none;
    border-radius: 10px; font-weight: 700;
    font-size: 0.95em; cursor: pointer;
    font-family: var(--font-body);
    transition: all 0.3s ease;
  }
  .sd-btn-primary { background: linear-gradient(135deg, var(--accent), var(--accent2)); color: white; }
  .sd-btn-primary:hover:not(:disabled)   { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(102,126,234,0.32); }
  .sd-btn-secondary { background: white; border: 2px solid var(--accent); color: var(--accent); }
  .sd-btn-secondary:hover:not(:disabled) { background: var(--accent); color: white; }
  .sd-btn-primary:disabled, .sd-btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }

  /* ── Empty state ── */
  .sd-empty { text-align: center; padding: 60px 20px; color: var(--muted); }
  .sd-empty-icon { font-size: 4em; display: block; margin-bottom: 16px; }
  .sd-empty strong { display: block; font-size: 1.1em; color: var(--dark); margin-bottom: 6px; }

  /* ── Loading spinner ── */
  .sd-loading { text-align: center; padding: 50px 20px; }
  .sd-spinner {
    width: 42px; height: 42px; margin: 0 auto 16px;
    border: 4px solid rgba(102,126,234,0.2);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.75s linear infinite;
  }
  .sd-loading p { color: var(--muted); font-weight: 600; }

  /* ── Result items ── */
  .sd-results {
    animation: fadeIn 0.3s ease-out;
    display: flex; flex-direction: column; gap: 12px;
    max-height: 480px; overflow-y: auto; padding-right: 4px;
  }
  .sd-results::-webkit-scrollbar { width: 5px; }
  .sd-results::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

  .sd-result-item {
    background: linear-gradient(135deg, #f9faff, #f5f2ff);
    padding: 16px; border-left: 5px solid var(--accent);
    border-radius: 10px; transition: all 0.25s ease;
  }
  .sd-result-item:hover { transform: translateX(4px); box-shadow: 0 6px 20px rgba(102,126,234,0.12); }
  .sd-result-item.obligation { border-left-color: #f39c12; background: linear-gradient(135deg, #fffaf0, #fff5e6); }

  .sd-item-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
  .sd-badge {
    padding: 3px 10px; border-radius: 6px;
    font-size: 0.82em; font-weight: 700;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: white;
  }
  .sd-badge.obl  { background: linear-gradient(135deg, #f39c12, #e67e22); }
  .sd-badge.conf { background: rgba(102,126,234,0.1); color: var(--accent); }
  .sd-item-text  { color: var(--dark); line-height: 1.65; font-size: 0.95em; }
  .sd-item-meta  { color: var(--muted); font-size: 0.83em; margin-top: 6px; }

  /* ── Entities ── */
  .sd-entity {
    display: flex; align-items: center; gap: 12px;
    padding: 11px 14px; background: #f9faff;
    border-radius: 10px; border: 2px solid var(--border);
    transition: all 0.25s ease;
  }
  .sd-entity:hover { border-color: var(--accent); background: #f0f4ff; }
  .sd-entity-badge {
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: white; padding: 3px 12px; border-radius: 20px;
    font-size: 0.78em; font-weight: 700; white-space: nowrap;
  }
  .sd-entity-text { flex: 1; color: var(--dark); font-weight: 600; font-size: 0.94em; }
  .sd-entity-conf { color: var(--accent); font-weight: 700; font-size: 0.88em; }

  /* ── Summary ── */
  .sd-summary { display: flex; flex-direction: column; gap: 18px; }
  .sd-summary-card {
    background: linear-gradient(135deg, #f9faff, #f5f2ff);
    padding: 22px; border-radius: 12px;
    border-left: 5px solid var(--accent);
  }
  .sd-summary-card h4 { color: var(--dark); margin-bottom: 14px; font-family: var(--font-display); font-size: 1.05em; }
  .sd-summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 14px; }
  .sd-summary-item { display: flex; flex-direction: column; gap: 5px; }
  .sd-summary-item .lbl { color: var(--muted); font-size: 0.87em; font-weight: 600; }
  .sd-summary-item .val { color: var(--accent); font-family: var(--font-display); font-size: 1.5em; font-weight: 800; }
  .sd-score-bar-bg { height: 8px; background: #e0e6ed; border-radius: 4px; overflow: hidden; margin-top: 6px; }
  .sd-score-bar    { height: 100%; border-radius: 4px; background: linear-gradient(90deg, var(--accent), var(--accent2)); animation: barGrow 0.8s ease-out; }
  .sd-summary-text { background: #f9faff; border: 1px solid var(--border); border-radius: 10px; padding: 16px; color: var(--dark); line-height: 1.7; font-size: 0.95em; }

  .sd-no-results { text-align: center; padding: 30px 20px; color: var(--muted); font-size: 0.93em; }

  /* ── Footer ── */
  .sd-footer {
    margin-top: 40px; padding: 18px 24px;
    background: linear-gradient(135deg, rgba(102,126,234,0.08), rgba(118,75,162,0.08));
    border-radius: 12px; border-left: 4px solid var(--accent);
    text-align: center; color: var(--muted); font-size: 0.9em;
  }

  /* ── Responsive ── */
  @media (max-width: 768px) {
    .sd-body     { padding: 20px; }
    .sd-banner   { padding: 30px 20px; }
    .sd-banner h1 { font-size: 2em; }
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
                    background: "linear-gradient(90deg,#2ecc71,#27ae60)",
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
      {/* ── Banner ── */}
      <div className="sd-banner">
        <h1>📄 SaralDoc</h1>
        <p>
          AI-powered Nepali / English legal document analyzer — get insights
          instantly
        </p>
      </div>

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

        {/* ── Footer ── */}
        <div className="sd-footer">
          🚀 SaralDoc — AI-powered legal document analysis. Results are
          informational only and do not constitute legal advice.
        </div>
      </div>
    </div>
  );
}
