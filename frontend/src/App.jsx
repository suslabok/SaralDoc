import { useState } from "react";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Analyzer from "./pages/Analyzer";
import History from "./pages/History";
import Settings from "./pages/Settings";
import "./App.css";

function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [isCollapsed, setIsCollapsed] = useState(false);

  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <Dashboard />;
      case "analyzer":
        return <Analyzer />;
      case "history":
        return <History />;
      case "settings":
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Navbar />
      <Sidebar
        onNavigate={setCurrentPage}
        currentPage={currentPage}
        isCollapsed={isCollapsed}
        onToggle={() => setIsCollapsed(!isCollapsed)}
      />
      <main className={`main-content ${isCollapsed ? "collapsed" : ""}`}>
        <div className="page-content">{renderPage()}</div>
      </main>
    </div>
  );
}

export default App;
