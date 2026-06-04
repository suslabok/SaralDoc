import { useState, useEffect } from "react";
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

    setSettings((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSave = () => {
    alert("Settings saved");
  };

  const handleReset = () => {
    setSettings({
      language: "en",
      theme: "light",
      notifications: true,
      autoSave: true,
      textSize: "normal",
    });
  };

  // Apply theme smoothly
  useEffect(() => {
    requestAnimationFrame(() => {
      document.documentElement.setAttribute("data-theme", settings.theme);
    });
  }, [settings.theme]);

  return (
    <div className="settings-page">
      <h2>Settings</h2>

      <div className="settings-section">
        <label>Language</label>
        <select
          name="language"
          value={settings.language}
          onChange={handleChange}
        >
          <option value="en">English</option>
          <option value="ne">Nepali</option>
          <option value="hi">Hindi</option>
        </select>

        <label>Theme</label>
        <select name="theme" value={settings.theme} onChange={handleChange}>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
          <option value="auto">Auto</option>
        </select>

        <label>Text Size</label>
        <select
          name="textSize"
          value={settings.textSize}
          onChange={handleChange}
        >
          <option value="small">Small</option>
          <option value="normal">Normal</option>
          <option value="large">Large</option>
          <option value="xlarge">Extra Large</option>
        </select>

        <label className="checkbox">
          <input
            type="checkbox"
            name="notifications"
            checked={settings.notifications}
            onChange={handleChange}
          />
          Notifications
        </label>

        <label className="checkbox">
          <input
            type="checkbox"
            name="autoSave"
            checked={settings.autoSave}
            onChange={handleChange}
          />
          Auto Save
        </label>
      </div>

      <div className="settings-actions">
        <button className="save-btn" onClick={handleSave}>
          Save Settings
        </button>
        <button className="reset-btn" onClick={handleReset}>
          Reset
        </button>
      </div>
    </div>
  );
}
