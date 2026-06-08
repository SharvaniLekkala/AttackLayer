import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import ChatPage from "./pages/ChatPage";
import DashboardPage from "./pages/DashboardPage";
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
        </Routes>
    );
}

export default App;
