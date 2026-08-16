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
        /* SIDEBAR - uses global tokens from main.css */
        .sidebar {
          position: fixed;
          top: 70px;
          left: 0;
          height: calc(100vh - 70px);
          width: 260px;
          background: var(--bg-card);
          color: var(--text-primary);
          border-right: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          transition: width 0.3s ease;
          overflow: hidden;
          z-index: 98;
        }

        .sidebar.collapsed {
          width: 80px;
        }

        /* HEADER */
        .sidebar-header {
          display: flex;
          align-items: center;
          justify-content: flex-end;
          padding: 14px;
          border-bottom: 1px solid var(--border);
        }

        .sidebar-toggle {
          width: 38px;
          height: 38px;
          border-radius: var(--radius-sm);
          border: 1px solid var(--border);
          background: var(--bg-primary);
          color: var(--text-primary);
          cursor: pointer;
          transition: border-color 0.2s ease;
        }

        .sidebar-toggle:hover {
          border-color: var(--border-active);
        }

        /* NAV */
        .sidebar-nav {
          display: flex;
          flex-direction: column;
          padding: 10px;
          gap: 6px;
          flex: 1;
        }

        .sidebar-link {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 10px 12px;
          border-radius: var(--radius-sm);
          border: none;
          background: transparent;
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.2s ease;
          font-size: 0.95rem;
          font-family: var(--font-body);
          text-align: left;
        }

        .sidebar-link:hover {
          background: var(--bg-primary);
          color: var(--text-primary);
        }

        .sidebar-link.active {
          background: var(--primary);
          color: #faf8f3;
        }

        .sidebar-icon {
          font-size: 1.15rem;
        }

        /* Hide text when collapsed */
        .sidebar.collapsed .sidebar-link-text {
          display: none;
        }

        /* FOOTER */
        .sidebar-footer {
          padding: 12px;
          border-top: 1px solid var(--border);
          text-align: center;
        }

        .version {
          font-size: 0.78rem;
          color: var(--text-muted);
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
