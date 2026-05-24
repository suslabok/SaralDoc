import { useState } from "react";
import "./Sidebar.css";

export default function Sidebar({
  onNavigate,
  currentPage,
  isCollapsed,
  onToggle,
}) {
  const [isExpanded, setIsExpanded] = useState(true);

  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: "📊" },
    { id: "history", label: "History", icon: "📜" },
    { id: "settings", label: "Settings", icon: "⚙️" },
  ];

  const handleNavClick = (pageId) => {
    onNavigate(pageId);
  };

  return (
    <aside className={`sidebar ${isCollapsed ? "collapsed" : ""}`}>
      <div className="sidebar-header">
        <button
          className="sidebar-toggle"
          onClick={onToggle}
          title={isCollapsed ? "Expand" : "Collapse"}
        >
          {isCollapsed ? "➜" : "⬅"}
        </button>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`sidebar-link ${
              currentPage === item.id ? "active" : ""
            }`}
            onClick={() => handleNavClick(item.id)}
            title={isCollapsed ? item.label : ""}
          >
            <span className="sidebar-icon">{item.icon}</span>
            <span className="sidebar-link-text">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-info">
          <p className="version">SaralDoc v2.0</p>
        </div>
      </div>
    </aside>
  );
}
