import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import ChatPage from "./pages/ChatPage";
import DashboardPage from "./pages/DashboardPage";
import MemoryVaultPage from "./pages/MemoryVaultPage";
import HITLPage from "./pages/HITLPage";
import ThreatAnalysisPage from "./pages/ThreatAnalysisPage";
import "./App.css";

function App() {
    return (
        <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route
                path="/chat"
                element={
                    <div className="app-shell">
                        <ChatPage />
                    </div>
                }
            />
            <Route
                path="/dashboard"
                element={
                    <Layout>
                        <DashboardPage />
                    </Layout>
                }
            />
            <Route
                path="/memory-vault"
                element={
                    <Layout>
                        <MemoryVaultPage />
                    </Layout>
                }
            />
            <Route
                path="/hitl"
                element={
                    <Layout>
                        <HITLPage />
                    </Layout>
                }
            />
            <Route
                path="/threat-analysis"
                element={
                    <Layout>
                        <ThreatAnalysisPage />
                    </Layout>
                }
            />
        </Routes>
    );
}

export default App;
