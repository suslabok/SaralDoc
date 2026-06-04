import { useState } from "react";
import "./Navbar.css";

export default function Navbar() {
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Left Section */}
        <div className="navbar-left">
          <button className="menu-toggle">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>

          <div className="navbar-logo">
            <span className="logo-icon">📜</span>
            <span className="logo-text">SaralDoc</span>
          </div>
        </div>

        {/* Center Section - Search */}
        <div className={`search-container ${isSearchFocused ? "focused" : ""}`}>
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="search-icon"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <input
            type="text"
            placeholder="Search documents..."
            className="search-input"
            onFocus={() => setIsSearchFocused(true)}
            onBlur={() => setIsSearchFocused(false)}
          />
        </div>

        {/* Right Section */}
        <div className="navbar-right">
          <div className="user-profile">
            <div className="user-avatar">👤</div>
            <span className="user-name">You</span>
          </div>
        </div>
      </div>
    </nav>
  );
}
