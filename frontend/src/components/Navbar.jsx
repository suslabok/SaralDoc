import { useState, useEffect } from "react";

export default function Navbar() {
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [theme, setTheme] = useState("light");

  // Load saved theme
  useEffect(() => {
    const saved = localStorage.getItem("theme") || "light";
    setTheme(saved);
    document.documentElement.setAttribute("data-theme", saved);
  }, []);

  // Toggle theme
  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.setAttribute("data-theme", newTheme);
  };

  return (
    <>
      <style>{`
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

        /* NAVBAR */
        .navbar {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          height: 70px;
          background: var(--card);
          color: var(--text);
          box-shadow: 0 10px 30px rgba(0,0,0,0.15);
          z-index: 99;
          display: flex;
          align-items: center;
          padding: 0 24px;
          transition: all 0.3s ease;
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
          background: var(--bg);
          color: var(--text);
          border: 1px solid var(--border);
          width: 40px;
          height: 40px;
          border-radius: 10px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .menu-toggle:hover {
          transform: scale(1.05);
        }

        .logo-text {
          font-weight: 800;
          background: linear-gradient(135deg, #667eea, #764ba2);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        /* SEARCH */
        .search-container {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px 14px;
          border-radius: 10px;
          background: var(--bg);
          border: 1px solid var(--border);
          width: 300px;
          transition: all 0.3s ease;
        }

        .search-container.focused {
          border-color: var(--primary);
          box-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
        }

        .search-input {
          border: none;
          outline: none;
          width: 100%;
          background: transparent;
          color: var(--text);
        }

        /* RIGHT */
        .navbar-right {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .theme-toggle {
          background: var(--bg);
          border: 1px solid var(--border);
          color: var(--text);
          width: 40px;
          height: 40px;
          border-radius: 10px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .theme-toggle:hover {
          transform: scale(1.05);
        }

        .user-profile {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 6px 10px;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 10px;
          color: var(--text);
        }

        .user-avatar {
          width: 32px;
          height: 32px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
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
            <div className="logo-text">SaralDoc</div>
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
            {/* THEME TOGGLE */}
            <button className="theme-toggle" onClick={toggleTheme}>
              {theme === "light" ? "🌙" : "☀️"}
            </button>

            {/* USER */}
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
