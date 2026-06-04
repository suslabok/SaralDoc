import React from "react";
import PropTypes from "prop-types";
import "./Sidebar.css";

export default function Sidebar({
  onNavigate = () => {},
  currentPage = "dashboard",
  isCollapsed = false,
  onToggle = () => {},
}) {
  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: "📊" },
    { id: "history", label: "History", icon: "📜" },
    { id: "settings", label: "Settings", icon: "⚙️" },
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
    <aside
      className={`sidebar ${isCollapsed ? "collapsed" : ""}`}
      aria-label="Primary navigation"
    >
      <div className="sidebar-header">
        <button
          className="sidebar-toggle"
          onClick={onToggle}
          aria-pressed={!!isCollapsed}
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          title={isCollapsed ? "Expand" : "Collapse"}
        >
          <span className="toggle-icon" aria-hidden>
            {isCollapsed ? "➜" : "⬅"}
          </span>
        </button>

        {!isCollapsed && (
          <div className="brand" aria-hidden>
            <strong>SaralDoc</strong>
          </div>
        )}
      </div>

      <nav className="sidebar-nav" role="menu">
        {menuItems.map((item) => {
          const active = currentPage === item.id;
          return (
            <button
              key={item.id}
              role="menuitem"
              tabIndex={0}
              className={`sidebar-link ${active ? "active" : ""}`}
              onClick={() => handleNav(item.id)}
              onKeyDown={(e) => handleKey(e, item.id)}
              aria-current={active ? "page" : undefined}
              title={isCollapsed ? item.label : ""}
            >
              <span className="sidebar-icon" aria-hidden>
                {item.icon}
              </span>
              <span className="sidebar-link-text">{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-info">
          <p className="version">v2.0</p>
        </div>
      </div>
    </aside>
  );
}

Sidebar.propTypes = {
  onNavigate: PropTypes.func,
  currentPage: PropTypes.string,
  isCollapsed: PropTypes.bool,
  onToggle: PropTypes.func,
};
