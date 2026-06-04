import React from "react";
import PropTypes from "prop-types";

export default function Sidebar({
  onNavigate = () => {},
  currentPage = "dashboard",
  isCollapsed = false,
  onToggle = () => {},
}) {
  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: "📊" },
    { id: "history", label: "History", icon: "📜" },
  ];

  const handleNav = (id) => {
    if (id !== currentPage) onNavigate(id);
  };

  const handleKey = (e, id) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleNav(id);
    }
  };

  return (
    <>
      <style>{`
        /* ================= THEME ================= */
        :root {
          --bg: #ffffff;
          --text: #111111;
          --card: #f5f5f5;
          --border: #e0e0e0;
          --primary: #4f46e5;
        }

        :root[data-theme="dark"] {
          --bg: #0f0f0f;
          --text: #ffffff;
          --card: #1a1a1a;
          --border: #2a2a2a;
          --primary: #6366f1;
        }

        /* ================= SIDEBAR ================= */
        .sidebar {
          position: fixed;
          top: 70px;
          left: 0;
          height: calc(100vh - 70px);
          width: 260px;
          background: var(--card);
          color: var(--text);
          border-right: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          transition: all 0.3s ease;
          overflow: hidden;
        }

        .sidebar.collapsed {
          width: 80px;
        }

        /* HEADER */
        .sidebar-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 14px;
          border-bottom: 1px solid var(--border);
        }

        .sidebar-toggle {
          width: 38px;
          height: 38px;
          border-radius: 10px;
          border: 1px solid var(--border);
          background: var(--bg);
          color: var(--text);
          cursor: pointer;
          transition: 0.3s ease;
        }

        .sidebar-toggle:hover {
          transform: scale(1.05);
        }

        .brand {
          font-weight: 700;
          font-size: 1.1rem;
        }

        /* NAV */
        .sidebar-nav {
          display: flex;
          flex-direction: column;
          padding: 10px;
          gap: 8px;
          flex: 1;
        }

        .sidebar-link {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 10px 12px;
          border-radius: 10px;
          border: none;
          background: transparent;
          color: var(--text);
          cursor: pointer;
          transition: all 0.25s ease;
          font-size: 0.95rem;
        }

        .sidebar-link:hover {
          background: var(--bg);
        }

        .sidebar-link.active {
          background: var(--primary);
          color: white;
        }

        .sidebar-icon {
          font-size: 1.2rem;
        }

        /* Hide text when collapsed */
        .sidebar.collapsed .sidebar-link-text {
          display: none;
        }

        .sidebar.collapsed .brand {
          display: none;
        }

        /* FOOTER */
        .sidebar-footer {
          padding: 12px;
          border-top: 1px solid var(--border);
          text-align: center;
        }

        .version {
          font-size: 0.8rem;
          opacity: 0.6;
        }

        /* SMOOTH TRANSITIONS */
        .sidebar,
        .sidebar-link,
        .sidebar-toggle {
          transition: all 0.3s ease;
        }
      `}</style>

      <aside className={`sidebar ${isCollapsed ? "collapsed" : ""}`}>
        {/* HEADER */}
        <div className="sidebar-header">
          <button
            className="sidebar-toggle"
            onClick={onToggle}
            aria-label="Toggle sidebar"
          >
            {isCollapsed ? "➜" : "⬅"}
          </button>

          {!isCollapsed && <div className="brand">SaralDoc</div>}
        </div>

        {/* NAV */}
        <nav className="sidebar-nav">
          {menuItems.map((item) => {
            const active = currentPage === item.id;

            return (
              <button
                key={item.id}
                className={`sidebar-link ${active ? "active" : ""}`}
                onClick={() => handleNav(item.id)}
                onKeyDown={(e) => handleKey(e, item.id)}
              >
                <span className="sidebar-icon">{item.icon}</span>
                <span className="sidebar-link-text">{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* FOOTER */}
        <div className="sidebar-footer">
          <div className="version">v2.0</div>
        </div>
      </aside>
    </>
  );
}

Sidebar.propTypes = {
  onNavigate: PropTypes.func,
  currentPage: PropTypes.string,
  isCollapsed: PropTypes.bool,
  onToggle: PropTypes.func,
};
