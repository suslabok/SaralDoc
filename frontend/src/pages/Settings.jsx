import { useState } from "react";
import "./Settings.css";

export default function Settings() {
  const [settings, setSettings] = useState({
    language: "en",
    theme: "light",
    notifications: true,
    autoSave: true,
    textSize: "normal",
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings({
      ...settings,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSave = () => {
    alert("Settings saved successfully!");
  };

  return (
    <div className="page settings-page">
      <header className="page-header">
        <h2>Settings</h2>
        <p>Customize your SaralDoc experience</p>
      </header>

      <div className="settings-container">
        <div className="settings-section">
          <h3>🌐 Language & Display</h3>
          <div className="setting-group">
            <label htmlFor="language">Language:</label>
            <select
              id="language"
              name="language"
              value={settings.language}
              onChange={handleChange}
              className="setting-input"
            >
              <option value="en">English</option>
              <option value="ne">Nepali</option>
              <option value="hi">Hindi</option>
            </select>
          </div>

          <div className="setting-group">
            <label htmlFor="theme">Theme:</label>
            <select
              id="theme"
              name="theme"
              value={settings.theme}
              onChange={handleChange}
              className="setting-input"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto</option>
            </select>
          </div>

          <div className="setting-group">
            <label htmlFor="textSize">Text Size:</label>
            <select
              id="textSize"
              name="textSize"
              value={settings.textSize}
              onChange={handleChange}
              className="setting-input"
            >
              <option value="small">Small</option>
              <option value="normal">Normal</option>
              <option value="large">Large</option>
              <option value="xlarge">Extra Large</option>
            </select>
          </div>
        </div>

        <div className="settings-section">
          <h3>🔔 Notifications & Behavior</h3>
          <div className="setting-group checkbox-group">
            <label>
              <input
                type="checkbox"
                name="notifications"
                checked={settings.notifications}
                onChange={handleChange}
              />
              Enable Notifications
            </label>
          </div>

          <div className="setting-group checkbox-group">
            <label>
              <input
                type="checkbox"
                name="autoSave"
                checked={settings.autoSave}
                onChange={handleChange}
              />
              Auto-save Analysis Results
            </label>
          </div>
        </div>

        <div className="settings-section">
          <h3>🔐 Privacy & Security</h3>
          <div className="setting-group">
            <p>
              Your documents are processed securely and not stored on servers.
            </p>
            <button className="secondary-btn">Clear Cache</button>
          </div>
          <div className="setting-group">
            <button className="secondary-btn">Download Your Data</button>
          </div>
        </div>

        <div className="settings-section">
          <h3>ℹ️ About</h3>
          <div className="about-content">
            <p>
              <strong>SaralDoc v1.0.0</strong>
            </p>
            <p>Legal Document Plain-Language Explainer</p>
            <p>
              <strong>Team:</strong> Akash Kafle, Sushma Acharya, Aayusha Jaspau
            </p>
            <p className="about-desc">
              Designed to extract and simplify legal content for government and
              administrative use. Efficiently analyzes Nepali contracts and
              legal documents.
            </p>
          </div>
        </div>

        <div className="settings-actions">
          <button className="primary-btn" onClick={handleSave}>
            💾 Save Settings
          </button>
          <button className="secondary-btn">Reset to Defaults</button>
        </div>
      </div>
    </div>
  );
}
