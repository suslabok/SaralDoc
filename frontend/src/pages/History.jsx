import { useState, useEffect } from "react";

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API = "http://localhost:8000";

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API}/history`);
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
    await fetch(`${API}/history/${id}`, { method: "DELETE" });
    setHistory((prev) => prev.filter((h) => h.id !== id));
  };

  const clearAll = async () => {
    if (!window.confirm("Clear all history?")) return;
    await fetch(`${API}/history`, { method: "DELETE" });
    setHistory([]);
  };

  const styles = {
    page: {
      padding: "30px",
      minHeight: "100vh",
      background: "var(--bg-primary)",
      fontFamily: "var(--font-body)",
    },

    header: {
      textAlign: "center",
      marginBottom: "20px",
    },

    title: {
      fontFamily: "var(--font-heading)",
      fontSize: "26px",
      fontWeight: "600",
      color: "var(--text-primary)",
    },

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

    filters: {
      display: "flex",
      gap: "10px",
      marginBottom: "15px",
    },

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

    table: {
      width: "100%",
      borderCollapse: "collapse",
    },

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

    stats: {
      display: "flex",
      gap: "10px",
      marginTop: "20px",
    },

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
  };

  if (loading) return <div style={styles.page}>Loading...</div>;

  return (
    <div style={styles.page}>
      {/* HEADER */}
      <div style={styles.header}>
        <h2 style={styles.title}>Analysis History</h2>
        <button style={styles.clearBtn} onClick={clearAll}>
          Clear All
        </button>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* FILTERS */}
      <div style={styles.filters}>
        <input style={styles.input} placeholder="Search..." />
        <select style={styles.select}>
          <option>All</option>
          <option>Contracts</option>
          <option>Agreements</option>
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
              <th style={styles.th}>Status</th>
              <th style={styles.th}>Action</th>
            </tr>
          </thead>

          <tbody>
            {history.map((item) => (
              <tr key={item.id}>
                <td style={styles.td}>📄 {item.name}</td>
                <td style={styles.td}>
                  {new Date(item.date).toLocaleDateString()}
                </td>
                <td style={styles.td}>
                  <span style={styles.badge}>{item.clauses}</span>
                </td>
                <td style={styles.td}>
                  <span style={styles.status}>{item.status}</span>
                </td>
                <td style={styles.td}>
                  <button
                    style={styles.deleteBtn}
                    onClick={() => deleteItem(item.id)}
                  >
                    🗑
                  </button>
                </td>
              </tr>
            ))}
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
            {history.reduce((a, b) => a + (b.clauses || 0), 0)}
          </div>
          <p>Total Clauses</p>
        </div>
      </div>
    </div>
  );
}
