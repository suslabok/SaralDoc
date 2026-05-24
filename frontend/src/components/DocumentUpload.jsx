import { useState } from "react";

export default function DocumentUpload({ onAnalyze, isLoading }) {
  const [text, setText] = useState("");
  const [fileName, setFileName] = useState("");

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (event) => {
      setText(event.target.result);
    };
    reader.readAsText(file);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim()) {
      onAnalyze(text);
    }
  };

  return (
    <div className="upload-box">
      <h2>Upload & Analyze Document</h2>
      <form onSubmit={handleSubmit}>
        <div className="upload-area">
          <label htmlFor="file-input" className="file-label">
            📁 Click to select or drag a file
          </label>
          <input
            id="file-input"
            type="file"
            accept=".txt,.pdf"
            onChange={handleFileUpload}
            className="file-input"
          />
          {fileName && <p className="file-name">Selected: {fileName}</p>}
        </div>

        <div className="text-input-section">
          <h3>Or paste Nepali legal text:</h3>
          <textarea
            value={text}
            onChange={handleTextChange}
            placeholder="Paste your Nepali legal document here..."
            rows="10"
            className="text-input"
          ></textarea>
        </div>

        <button
          type="submit"
          disabled={isLoading || !text.trim()}
          className="analyze-btn"
        >
          {isLoading ? "Analyzing..." : "Analyze Document"}
        </button>
      </form>
    </div>
  );
}
