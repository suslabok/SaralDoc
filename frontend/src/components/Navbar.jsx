import { useState, useEffect, useRef } from "react";
import { useAuth, API } from "../context/AuthContext";

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

export default function Navbar() {
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [isDark, setIsDark] = useState(
    () => document.documentElement.getAttribute("data-theme") === "dark",
  );
  const { user, loading: authLoading, setUser, logout } = useAuth();
  const [authError, setAuthError] = useState(null);
  const googleButtonRef = useRef(null);

  useEffect(() => {
    document.documentElement.setAttribute(
      "data-theme",
      isDark ? "dark" : "light",
    );
    localStorage.setItem("saraldoc-theme", isDark ? "dark" : "light");
  }, [isDark]);

  const handleCredentialResponse = async (response) => {
    setAuthError(null);
    try {
      const res = await fetch(`${API}/auth/google`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ credential: response.credential }),
      });
      if (!res.ok) {
        let detail = `HTTP ${res.status}`;
        try {
          const body = await res.json();
          if (body.detail) detail = body.detail;
        } catch {
          // response wasn't JSON, keep the plain status
        }
        throw new Error(detail);
      }
      const data = await res.json();
      setUser(data.user);
    } catch (err) {
      console.error("Google sign-in failed:", err);
      setAuthError(
        err.message === "Failed to fetch"
          ? `Could not reach the backend at ${API}. Is it running?`
          : err.message,
      );
    }
  };

  // Render Google's own Sign In button once the GIS script has loaded and
  // the user isn't already signed in. The script tag in index.html loads
  // asynchronously, so we poll briefly for window.google to exist.
  useEffect(() => {
    if (user || authLoading) return;
    if (!GOOGLE_CLIENT_ID) {
      console.warn(
        "VITE_GOOGLE_CLIENT_ID is not set - Google Sign-In button will not render.",
      );
      return;
    }

    let attempts = 0;
    const tryRender = () => {
      attempts += 1;
      if (window.google?.accounts?.id && googleButtonRef.current) {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleCredentialResponse,
        });
        window.google.accounts.id.renderButton(googleButtonRef.current, {
          theme: "outline",
          size: "medium",
          shape: "pill",
          text: "signin",
        });
      } else if (attempts < 40) {
        setTimeout(tryRender, 100);
      }
    };
    tryRender();
  }, [user, authLoading]);

  const handleLogout = async () => {
    await logout(); // from AuthContext - hits /auth/logout and clears user everywhere
  };

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
          box-shadow: 0 0 0 3px rgba(61, 90, 128, 0.1);
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
          min-height: 40px;
          padding: 6px 12px;
          background: var(--bg-primary);
          border: 1px solid var(--border);
          border-radius: var(--radius-sm);
          color: var(--text-primary);
          font-size: 0.9rem;
        }

        .user-profile:has(.auth-slot) {
          background: transparent;
          border: none;
          padding: 0;
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

        .user-avatar-img {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          object-fit: cover;
        }

        .auth-slot {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .auth-error {
          font-size: 0.78rem;
          color: var(--risk-high);
          max-width: 220px;
        }

        .logout-btn {
          background: transparent;
          border: 1px solid var(--border);
          color: var(--text-secondary);
          font-size: 0.82rem;
          padding: 5px 10px;
          border-radius: var(--radius-sm);
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .logout-btn:hover {
          border-color: var(--border-active);
          color: var(--primary);
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
              {!authLoading && user ? (
                <>
                  {user.picture ? (
                    <img
                      src={user.picture}
                      alt={user.name}
                      className="user-avatar-img"
                    />
                  ) : (
                    <div className="user-avatar">👤</div>
                  )}
                  <span>{user.name || user.email}</span>
                  <button className="logout-btn" onClick={handleLogout}>
                    Sign out
                  </button>
                </>
              ) : (
                <div className="auth-slot">
                  <div ref={googleButtonRef} />
                  {authError && <span className="auth-error">{authError}</span>}
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>
    </>
  );
}
