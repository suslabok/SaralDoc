import { useState } from "react";
import { Routes, Route, useLocation, useNavigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import "./App.css";

function App() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Sidebar still works with a simple page id ("dashboard" | "history");
  // we translate that to/from real URLs here so Sidebar doesn't need to
  // know about routing.
  const currentPage =
    location.pathname === "/history" ? "history" : "dashboard";
  const goToPage = (page) => navigate(page === "history" ? "/history" : "/");

  return (
    <div className={`app-root ${isCollapsed ? "sidebar-collapsed" : ""}`}>
      <Navbar />

      <Sidebar
        currentPage={currentPage}
        onNavigate={goToPage}
        isCollapsed={isCollapsed}
        onToggle={() => setIsCollapsed((prev) => !prev)}
      />

      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/history" element={<History />} />
          <Route path="*" element={<Dashboard />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
