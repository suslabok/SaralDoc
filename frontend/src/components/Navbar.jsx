import { useState, useEffect } from "react";

export default function Navbar() {
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [isDark, setIsDark] = useState(
    () => document.documentElement.getAttribute("data-theme") === "dark",
  );

  useEffect(() => {
    document.documentElement.setAttribute(
      "data-theme",
      isDark ? "dark" : "light",
    );
    localStorage.setItem("saraldoc-theme", isDark ? "dark" : "light");
  }, [isDark]);

  return (
    <>
      <style>{`
        /* NAVBAR - uses global tokens from main.css */
        .navbar {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          height: 70px;
          background: var(--bg-card);
          color: var(--text-primary);
          border-bottom: 1px solid var(--border);
          z-index: 99;
          display: flex;
          align-items: center;
          padding: 0 24px;
        }

        .navbar-container {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;
          max-width: 1400px;
          margin: 0 auto;
        }

        /* LEFT */
        .navbar-left {
          display: flex;
          align-items: center;
          gap: 14px;
        }

        .menu-toggle {
          background: var(--bg-primary);
          color: var(--text-primary);
          border: 1px solid var(--border);
          width: 40px;
          height: 40px;
          border-radius: var(--radius-sm);
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .menu-toggle:hover {
          border-color: var(--border-active);
        }

        .logo-text {
          display: flex;
          align-items: center;
          gap: 8px;
          font-family: var(--font-heading);
          font-weight: 600;
          font-size: 1.2rem;
          color: var(--primary);
          letter-spacing: 0.2px;
        }

        .logo-img {
          width: 40px;
          height: 40px;
          object-fit: contain;
        }

        /* SEARCH */
        .search-container {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px 14px;
          border-radius: var(--radius-sm);
          background: var(--bg-primary);
          border: 1px solid var(--border);
          width: 300px;
          transition: all 0.2s ease;
        }

        .search-container.focused {
          border-color: var(--primary);
          box-shadow: 0 0 0 3px rgba(168, 73, 46, 0.1);
        }

        .search-input {
          border: none;
          outline: none;
          width: 100%;
          background: transparent;
          color: var(--text-primary);
          font-family: var(--font-body);
        }

        .theme-toggle {
          width: 40px;
          height: 40px;
          background: var(--bg-primary);
          color: var(--text-primary);
          border: 1px solid var(--border);
          border-radius: var(--radius-sm);
          cursor: pointer;
          font-size: 1.1rem;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
        }

        .theme-toggle:hover {
          border-color: var(--border-active);
        }

        /* RIGHT */
        .navbar-right {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .user-profile {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 6px 12px;
          background: var(--bg-primary);
          border: 1px solid var(--border);
          border-radius: var(--radius-sm);
          color: var(--text-primary);
          font-size: 0.9rem;
        }

        .user-avatar {
          width: 32px;
          height: 32px;
          background: var(--primary);
          border-radius: var(--radius-sm);
          display: flex;
          align-items: center;
          justify-content: center;
          color: #faf8f3;
        }

        /* RESPONSIVE */
        @media (max-width: 768px) {
          .search-container {
            display: none;
          }
        }
      `}</style>

      <nav className="navbar">
        <div className="navbar-container">
          {/* LEFT */}
          <div className="navbar-left">
            <div className="logo-text">
              <img src="/logo.png" alt="SaralDoc" className="logo-img" />
              SaralDoc
            </div>
          </div>

          {/* SEARCH */}
          <div
            className={`search-container ${isSearchFocused ? "focused" : ""}`}
          >
            🔍
            <input
              className="search-input"
              placeholder="Search documents..."
              onFocus={() => setIsSearchFocused(true)}
              onBlur={() => setIsSearchFocused(false)}
            />
          </div>

          {/* RIGHT */}
          <div className="navbar-right">
            <button
              className="theme-toggle"
              onClick={() => setIsDark((prev) => !prev)}
              aria-label="Toggle dark mode"
              title={isDark ? "Switch to light mode" : "Switch to dark mode"}
            >
              {isDark ? "☀️" : "🌙"}
            </button>
            <div className="user-profile">
              <div className="user-avatar">👤</div>
              <span>You</span>
            </div>
          </div>
        </div>
      </nav>
    </>
  );
}
