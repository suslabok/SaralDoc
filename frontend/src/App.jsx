import { useState } from "react";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import "./App.css";

function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [isCollapsed, setIsCollapsed] = useState(false);

  const renderPage = () => {
    switch (currentPage) {
      case "history":
        return <History />;
      case "dashboard":
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className={`app-root ${isCollapsed ? "sidebar-collapsed" : ""}`}>
      <Navbar />

      <Sidebar
        currentPage={currentPage}
        onNavigate={setCurrentPage}
        isCollapsed={isCollapsed}
        onToggle={() => setIsCollapsed((prev) => !prev)}
      />

      <main className="main">{renderPage()}</main>
    </div>
  );
}

export default App;
