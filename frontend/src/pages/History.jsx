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
      background: "#f5f7fa",
      fontFamily: "sans-serif",
    },

    header: {
      textAlign: "center",
      marginBottom: "20px",
    },

    title: {
      fontSize: "28px",
      fontWeight: "900",
      background: "linear-gradient(135deg,#667eea,#764ba2)",
      WebkitBackgroundClip: "text",
      WebkitTextFillColor: "transparent",
    },

    clearBtn: {
      marginTop: "10px",
      padding: "8px 14px",
      border: "none",
      borderRadius: "8px",
      background: "crimson",
      color: "white",
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
      borderRadius: "8px",
      border: "1px solid #ddd",
    },

    select: {
      padding: "10px",
      borderRadius: "8px",
      border: "1px solid #ddd",
    },

    tableBox: {
      background: "white",
      borderRadius: "10px",
      overflow: "hidden",
      boxShadow: "0 5px 15px rgba(0,0,0,0.08)",
    },

    table: {
      width: "100%",
      borderCollapse: "collapse",
    },

    th: {
      background: "linear-gradient(135deg,#667eea,#764ba2)",
      color: "white",
      padding: "12px",
      textAlign: "left",
    },

    td: {
      padding: "12px",
      borderBottom: "1px solid #eee",
    },

    badge: {
      background: "#eef2ff",
      padding: "4px 10px",
      borderRadius: "12px",
      color: "#667eea",
      fontWeight: "bold",
    },

    status: {
      background: "#e6f7e6",
      padding: "4px 10px",
      borderRadius: "12px",
      color: "green",
      fontWeight: "bold",
    },

    deleteBtn: {
      padding: "6px 10px",
      border: "none",
      background: "#ffdddd",
      color: "#c00",
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
      background: "white",
      padding: "15px",
      borderRadius: "10px",
      textAlign: "center",
    },

    number: {
      fontSize: "22px",
      color: "#667eea",
      fontWeight: "bold",
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
