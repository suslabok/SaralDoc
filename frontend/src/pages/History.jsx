import { useState, useEffect, useMemo } from "react";
import { useAuth, API } from "../context/AuthContext";

export default function History() {
  const { user, loading: authLoading } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [languageFilter, setLanguageFilter] = useState("all");

  useEffect(() => {
    if (authLoading) return; // wait to know sign-in state before deciding what to fetch
    if (!user) {
      setLoading(false);
      setHistory([]);
      return;
    }
    fetchHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, authLoading]);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`${API}/history`, { credentials: "include" });
      if (res.status === 401) {
        // session expired mid-visit
        setHistory([]);
        setError("Your session expired. Please sign in again.");
        return;
      }
      const data = await res.json();
      if (data.success) setHistory(data.history || []);
      else setError(data.error || "Failed to load history");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteItem = async (id) => {
    const prev = history;
    setHistory((h) => h.filter((item) => item.id !== id)); // optimistic
    try {
      const res = await fetch(`${API}/history/${id}`, {
        method: "DELETE",
        credentials: "include",
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || "Delete failed");
    } catch (err) {
      setHistory(prev); // roll back on failure
      setError(err.message);
    }
  };

  const clearAll = async () => {
    if (!window.confirm(`Delete all ${history.length} analyses? This can't be undone.`)) return;
    const prev = history;
    setHistory([]);
    try {
      const res = await fetch(`${API}/history`, {
        method: "DELETE",
        credentials: "include",
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || "Clear failed");
    } catch (err) {
      setHistory(prev);
      setError(err.message);
    }
  };

  const languageOptions = useMemo(() => {
    const set = new Set(history.map((h) => h.language).filter(Boolean));
    return ["all", ...Array.from(set)];
  }, [history]);

  const filtered = useMemo(() => {
    return history.filter((item) => {
      const matchesSearch = !searchTerm.trim()
        || (item.document_name || "").toLowerCase().includes(searchTerm.trim().toLowerCase());
      const matchesLang = languageFilter === "all" || item.language === languageFilter;
      return matchesSearch && matchesLang;
    });
  }, [history, searchTerm, languageFilter]);

  const styles = {
    page: {
      padding: "30px",
      minHeight: "100vh",
      background: "var(--bg-primary)",
      fontFamily: "var(--font-body)",
    },
    header: { textAlign: "center", marginBottom: "20px" },
    title: {
      fontFamily: "var(--font-heading)",
      fontSize: "26px",
      fontWeight: "600",
      color: "var(--text-primary)",
    },
    subtitle: { color: "var(--text-secondary)", marginTop: "6px", fontSize: "0.9em" },
    clearBtn: {
      marginTop: "10px",
      padding: "8px 16px",
      border: "1px solid var(--border-active)",
      borderRadius: "6px",
      background: "transparent",
      color: "var(--primary)",
      fontWeight: "600",
      cursor: "pointer",
    },
    filters: { display: "flex", gap: "10px", marginBottom: "15px" },
    input: {
      flex: 1,
      padding: "10px",
      borderRadius: "6px",
      border: "1px solid var(--border)",
      background: "var(--bg-card)",
      color: "var(--text-primary)",
    },
    select: {
      padding: "10px",
      borderRadius: "6px",
      border: "1px solid var(--border)",
      background: "var(--bg-card)",
      color: "var(--text-primary)",
    },
    tableBox: {
      background: "var(--bg-card)",
      borderRadius: "10px",
      overflow: "hidden",
      border: "1px solid var(--border)",
      boxShadow: "var(--shadow-sm)",
    },
    table: { width: "100%", borderCollapse: "collapse" },
    th: {
      background: "var(--text-primary)",
      color: "var(--bg-card)",
      padding: "12px",
      textAlign: "left",
      fontWeight: "600",
      fontSize: "0.9em",
    },
    td: {
      padding: "12px",
      borderBottom: "1px solid var(--border)",
      color: "var(--text-primary)",
    },
    badge: {
      background: "rgba(168,73,46,0.1)",
      padding: "4px 10px",
      borderRadius: "999px",
      color: "var(--primary)",
      fontWeight: "600",
      fontSize: "0.85em",
    },
    status: {
      background: "rgba(63,92,74,0.12)",
      padding: "4px 10px",
      borderRadius: "999px",
      color: "var(--secondary)",
      fontWeight: "600",
      fontSize: "0.85em",
    },
    deleteBtn: {
      padding: "6px 10px",
      border: "1px solid var(--border-active)",
      background: "transparent",
      color: "var(--primary)",
      borderRadius: "6px",
      cursor: "pointer",
    },
    stats: { display: "flex", gap: "10px", marginTop: "20px" },
    card: {
      flex: 1,
      background: "var(--bg-card)",
      padding: "15px",
      borderRadius: "10px",
      border: "1px solid var(--border)",
      textAlign: "center",
    },
    number: {
      fontFamily: "var(--font-heading)",
      fontSize: "22px",
      color: "var(--primary)",
      fontWeight: "600",
    },
    emptyState: {
      padding: "50px 20px",
      textAlign: "center",
      color: "var(--text-secondary)",
    },
  };

  if (authLoading) return <div style={styles.page}>Loading…</div>;

  if (!user) {
    return (
      <div style={styles.page}>
        <div style={styles.header}>
          <h2 style={styles.title}>Analysis History</h2>
        </div>
        <div style={{ ...styles.tableBox, ...styles.emptyState }}>
          <p style={{ marginBottom: "8px", fontSize: "1.05em" }}>
            Sign in to view your analysis history
          </p>
          <p style={{ fontSize: "0.88em" }}>
            Use the sign-in button in the top-right corner. Analyses you run
            while signed in are saved here automatically.
          </p>
        </div>
      </div>
    );
  }

  if (loading) return <div style={styles.page}>Loading your history…</div>;

  return (
    <div style={styles.page}>
      {/* HEADER */}
      <div style={styles.header}>
        <h2 style={styles.title}>Analysis History</h2>
        <p style={styles.subtitle}>Signed in as {user.name || user.email}</p>
        {history.length > 0 && (
          <button style={styles.clearBtn} onClick={clearAll}>
            Clear All
          </button>
        )}
      </div>

      {error && <p style={{ color: "var(--risk-high, red)", textAlign: "center", marginBottom: "12px" }}>{error}</p>}

      {history.length === 0 ? (
        <div style={{ ...styles.tableBox, ...styles.emptyState }}>
          <p style={{ fontSize: "1.05em" }}>No analyses yet</p>
          <p style={{ fontSize: "0.88em", marginTop: "6px" }}>
            Analyze a document from the Dashboard and it'll show up here.
          </p>
        </div>
      ) : (
        <>
          {/* FILTERS */}
          <div style={styles.filters}>
            <input
              style={styles.input}
              placeholder="Search by document name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <select
              style={styles.select}
              value={languageFilter}
              onChange={(e) => setLanguageFilter(e.target.value)}
            >
              {languageOptions.map((lang) => (
                <option key={lang} value={lang}>
                  {lang === "all" ? "All languages" : lang}
                </option>
              ))}
            </select>
          </div>

          {/* TABLE */}
          <div style={styles.tableBox}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Document</th>
                  <th style={styles.th}>Date</th>
                  <th style={styles.th}>Clauses</th>
                  <th style={styles.th}>Language</th>
                  <th style={styles.th}>Action</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((item) => (
                  <tr key={item.id}>
                    <td style={styles.td}>📄 {item.document_name}</td>
                    <td style={styles.td}>
                      {new Date(item.timestamp).toLocaleDateString()}
                    </td>
                    <td style={styles.td}>
                      <span style={styles.badge}>{item.clauses_count}</span>
                    </td>
                    <td style={styles.td}>
                      <span style={styles.status}>{item.language}</span>
                    </td>
                    <td style={styles.td}>
                      <button
                        style={styles.deleteBtn}
                        onClick={() => deleteItem(item.id)}
                        aria-label={`Delete ${item.document_name}`}
                      >
                        🗑
                      </button>
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td style={styles.td} colSpan={5}>
                      No results match your filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* STATS */}
          <div style={styles.stats}>
            <div style={styles.card}>
              <div style={styles.number}>{history.length}</div>
              <p>Documents</p>
            </div>
            <div style={styles.card}>
              <div style={styles.number}>
                {history.reduce((a, b) => a + (b.clauses_count || 0), 0)}
              </div>
              <p>Total Clauses</p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
