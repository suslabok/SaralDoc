import { useState, useRef } from "react";
import "./Dashboard.css";

export default function Dashboard() {
  const [inputMethod, setInputMethod] = useState("upload");
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("clauses");
  const fileInputRef = useRef(null);

  const API_BASE = "http://localhost:8000";

  const handleTextChange = (e) => {
    setText(e.target.value);
    setError(null);
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const validTypes = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
      ];
      if (!validTypes.includes(selectedFile.type)) {
        setError("Only PDF, DOCX, and TXT files are supported");
        return;
      }
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB");
        return;
      }
      setFile(selectedFile);
      setText("");
      setError(null);
    }
  };

  const handleAnalyzeText = async () => {
    if (!text.trim()) {
      setError("Please paste some text");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          language: "auto",
          extract_summary: true,
        }),
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);
      const data = await response.json();

      if (data.success) {
        setResults(data);
        setActiveTab("clauses");
      } else {
        setError(data.error || "Analysis failed");
      }
    } catch (err) {
      setError(`Error: ${err.message}. Make sure backend is running.`);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeFile = async () => {
    if (!file) {
      setError("Please select a file");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/analyze-file`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);
      const data = await response.json();

      if (data.success) {
        setResults(data);
        setActiveTab("clauses");
      } else {
        setError(data.error || "File analysis failed");
      }
    } catch (err) {
      setError(`Error: ${err.message}. Make sure backend is running.`);
    } finally {
      setLoading(false);
    }
  };

  const handleClearAll = () => {
    setText("");
    setFile(null);
    setResults(null);
    setError(null);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.classList.add("drag-over");
  };

  const handleDragLeave = (e) => {
    e.currentTarget.classList.remove("drag-over");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove("drag-over");
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect({ target: { files: [droppedFile] } });
    }
  };

  return (
    <div className="dashboard-page">
      {/* Welcome Banner */}
      <div className="dashboard-welcome">
        <div className="welcome-content">
          <h1 className="welcome-title">🚀 Welcome to SaralDoc</h1>
          <p className="welcome-subtitle">
            AI-powered legal document analyzer - Get insights instantly
          </p>
        </div>
      </div>

      {/* Main Analyzer Section */}
      <div className="analyzer-section">
        <div className="analyzer-container">
          {/* Input Section */}
          <div className="input-section">
            <div className="section-header">
              <span>📋 Analyze Document</span>
            </div>

            <div className="input-tabs">
              <button
                className={`tab-btn ${
                  inputMethod === "upload" ? "active" : ""
                }`}
                onClick={() => {
                  setInputMethod("upload");
                  setText("");
                }}
              >
                📤 Upload File
              </button>
              <button
                className={`tab-btn ${inputMethod === "paste" ? "active" : ""}`}
                onClick={() => {
                  setInputMethod("paste");
                  setFile(null);
                }}
              >
                ✍️ Paste Text
              </button>
            </div>

            {error && (
              <div className="error-alert">
                <span>⚠️</span>
                <p>{error}</p>
                <button onClick={() => setError(null)}>✕</button>
              </div>
            )}

            {inputMethod === "upload" ? (
              <div
                className="upload-area"
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div className="upload-icon">📁</div>
                <h3>Drag & drop your file here</h3>
                <p>or click to browse</p>
                <p className="upload-hint">
                  Supported: PDF, DOCX, TXT (max 10MB)
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={handleFileSelect}
                  accept=".pdf,.docx,.txt"
                  style={{ display: "none" }}
                  disabled={loading}
                />
                <button
                  type="button"
                  className="browse-btn"
                  onClick={() => fileInputRef.current?.click()}
                >
                  Browse Files
                </button>
                {file && (
                  <div className="file-selected">
                    <span>✓ Selected: {file.name}</span>
                    <button onClick={() => setFile(null)} type="button">
                      ✕
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <textarea
                value={text}
                onChange={handleTextChange}
                placeholder="Paste your legal document here..."
                className="text-area"
                disabled={loading}
              />
            )}

            <div className="action-buttons">
              <button
                className="btn-primary"
                onClick={
                  inputMethod === "paste"
                    ? handleAnalyzeText
                    : handleAnalyzeFile
                }
                disabled={
                  loading || (inputMethod === "paste" ? !text.trim() : !file)
                }
              >
                {loading ? "⏳ Analyzing..." : "🚀 Analyze"}
              </button>
              <button
                className="btn-secondary"
                onClick={handleClearAll}
                disabled={loading}
              >
                Clear
              </button>
            </div>
          </div>

          {/* Results Section */}
          <div className="results-section">
            <div className="section-header">
              <span>📊 Results</span>
            </div>

            {!results ? (
              <div className="empty-state">
                <div className="empty-icon">📋</div>
                <p>No results yet</p>
                <small>Upload or paste a document to analyze</small>
              </div>
            ) : (
              <div>
                <div className="results-tabs">
                  <button
                    className={`result-tab ${
                      activeTab === "clauses" ? "active" : ""
                    }`}
                    onClick={() => setActiveTab("clauses")}
                  >
                    📄 Clauses ({results.clauses?.length || 0})
                  </button>
                  <button
                    className={`result-tab ${
                      activeTab === "obligations" ? "active" : ""
                    }`}
                    onClick={() => setActiveTab("obligations")}
                  >
                    ⚖️ Obligations ({results.obligations?.length || 0})
                  </button>
                  <button
                    className={`result-tab ${
                      activeTab === "entities" ? "active" : ""
                    }`}
                    onClick={() => setActiveTab("entities")}
                  >
                    👥 Entities ({results.entities?.length || 0})
                  </button>
                  <button
                    className={`result-tab ${
                      activeTab === "summary" ? "active" : ""
                    }`}
                    onClick={() => setActiveTab("summary")}
                  >
                    📈 Summary
                  </button>
                </div>

                <div className="results-content">
                  {activeTab === "clauses" && (
                    <div>
                      {results.clauses && results.clauses.length > 0 ? (
                        <div className="clauses-list">
                          {results.clauses.map((clause, idx) => (
                            <div key={idx} className="result-item">
                              <div className="item-header">
                                <span className="item-number">#{idx + 1}</span>
                                <span className="item-confidence">
                                  {(clause.confidence * 100).toFixed(0)}%
                                </span>
                              </div>
                              <p className="item-text">{clause.clause}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="no-results">No clauses found</div>
                      )}
                    </div>
                  )}

                  {activeTab === "obligations" && (
                    <div>
                      {results.obligations && results.obligations.length > 0 ? (
                        <div className="obligations-list">
                          {results.obligations.map((obligation, idx) => (
                            <div key={idx} className="result-item obligation">
                              <div className="item-header">
                                <span className="obligation-type">
                                  {obligation.type}
                                </span>
                                <span className="item-confidence">
                                  {(obligation.confidence * 100).toFixed(0)}%
                                </span>
                              </div>
                              <p className="item-text">
                                {obligation.obligation}
                              </p>
                              <small>Language: {obligation.language}</small>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="no-results">No obligations found</div>
                      )}
                    </div>
                  )}

                  {activeTab === "entities" && (
                    <div>
                      {results.entities && results.entities.length > 0 ? (
                        <div className="entities-list">
                          {results.entities.map((entity, idx) => (
                            <div key={idx} className="entity-item">
                              <span className="entity-badge">
                                {entity.type}
                              </span>
                              <span className="entity-text">{entity.text}</span>
                              <span className="entity-confidence">
                                {(entity.confidence * 100).toFixed(0)}%
                              </span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="no-results">No entities found</div>
                      )}
                    </div>
                  )}

                  {activeTab === "summary" && (
                    <div className="summary-content">
                      <div className="summary-card">
                        <h4>Document Info</h4>
                        <div className="summary-grid">
                          <div className="summary-item">
                            <span className="label">Language:</span>
                            <span className="value">{results.language}</span>
                          </div>
                          <div className="summary-item">
                            <span className="label">Complexity:</span>
                            <span className="value">
                              {results.complexity_score}/100
                            </span>
                          </div>
                          <div className="summary-item">
                            <span className="label">Readability:</span>
                            <span className="value">
                              {results.readability_score}/100
                            </span>
                          </div>
                        </div>
                      </div>
                      {results.summary && (
                        <div className="summary-card">
                          <h4>Summary</h4>
                          <p>{results.summary}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="features-section">
        <h2 className="section-title">✨ Key Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🚀</div>
            <h3>Fast Analysis</h3>
            <p>Analyze documents in seconds with AI</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🌍</div>
            <h3>Multi-Language</h3>
            <p>Supports Nepali, English & mixed text</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>Deep Insights</h3>
            <p>Extract clauses, obligations & entities</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📈</div>
            <h3>Smart Scoring</h3>
            <p>Complexity & readability analysis</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="dashboard-footer">
        <p>
          💡 Tip: Drag and drop your documents or paste text to get instant AI
          analysis
        </p>
      </div>
    </div>
  );
}
