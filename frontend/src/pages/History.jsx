import "./History.css";

export default function History() {
  const history = [
    {
      id: 1,
      name: "Government Contract 001",
      date: "2024-01-15",
      clauses: 24,
      status: "completed",
    },
    {
      id: 2,
      name: "Employment Agreement",
      date: "2024-01-14",
      clauses: 18,
      status: "completed",
    },
    {
      id: 3,
      name: "Service Agreement",
      date: "2024-01-13",
      clauses: 15,
      status: "completed",
    },
    {
      id: 4,
      name: "Loan Agreement",
      date: "2024-01-12",
      clauses: 32,
      status: "completed",
    },
    {
      id: 5,
      name: "Partnership Contract",
      date: "2024-01-11",
      clauses: 28,
      status: "completed",
    },
  ];

  return (
    <div className="page history-page">
      <header className="page-header">
        <h2>Analysis History</h2>
        <p>View all previously analyzed documents</p>
      </header>

      <div className="history-container">
        <div className="filters">
          <input
            type="text"
            placeholder="Search documents..."
            className="search-input"
          />
          <select className="filter-select">
            <option>All Documents</option>
            <option>Contracts</option>
            <option>Agreements</option>
            <option>Policies</option>
          </select>
        </div>

        <div className="history-table">
          <table>
            <thead>
              <tr>
                <th>Document Name</th>
                <th>Date</th>
                <th>Clauses Found</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.id}>
                  <td className="doc-name">
                    <span className="doc-icon">📄</span> {item.name}
                  </td>
                  <td>{item.date}</td>
                  <td>
                    <span className="clause-badge">{item.clauses}</span>
                  </td>
                  <td>
                    <span className={`status-badge ${item.status}`}>
                      ✓ {item.status}
                    </span>
                  </td>
                  <td>
                    <button className="action-btn view-btn">👁️ View</button>
                    <button className="action-btn delete-btn">🗑️ Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="history-stats">
          <div className="stat">
            <span className="stat-num">5</span>
            <span className="stat-label">Documents Analyzed</span>
          </div>
          <div className="stat">
            <span className="stat-num">117</span>
            <span className="stat-label">Total Clauses</span>
          </div>
          <div className="stat">
            <span className="stat-num">2.3s</span>
            <span className="stat-label">Avg Processing Time</span>
          </div>
        </div>
      </div>
    </div>
  );
}
