import { useState, useEffect } from "react";
import MemoryTable from "../components/dashboard/MemoryTable";
import AuditTable from "../components/dashboard/AuditTable";
import {
    clearDatabases,
    downloadExcel,
    getAllMemories,
    getAuditEvents
} from "../api/attacklayer";
import "../styles/dashboard.css";

function DashboardPage() {

    const [memories, setMemories] = useState([]);
    const [events, setEvents] = useState([]);
    const [isClearing, setIsClearing] = useState(false);
    const [status, setStatus] = useState("");
    const averageTrust =
        memories.length > 0
            ? (
                memories.reduce(
                    (sum, memory) =>
                        sum + (memory.trust_score || 0),
                    0
                ) / memories.length
            ).toFixed(2)
            : "0.00";

    const allowedCount = events.filter(
        (event) =>
            (event.final_decision ?? event.decision) ===
            "ALLOW"
    ).length;

    const blockedCount = events.filter(
        (event) =>
            (event.final_decision ?? event.decision) ===
            "BLOCK"
    ).length;

    const warningCount = events.filter((event) =>
        ["ALLOW_WITH_WARNING", "REVIEW"].includes(
            event.final_decision ?? event.decision
        )
    ).length;
    useEffect(() => {
        loadDashboard();
        const timer = setInterval(loadDashboard, 5000);
        return () => clearInterval(timer);
    }, []);

    async function loadDashboard() {
        try {
            const [memory, audit] = await Promise.all([
                getAllMemories(),
                getAuditEvents()
            ]);
            setMemories(memory);
            setEvents(audit);
        } catch (error) {
            console.log(error);
        }
    }

    async function handleClearDatabases() {
        const confirmed = window.confirm(
            "Clear all AttackLayer database records and Chroma memory data? This cannot be undone."
        );
        if (!confirmed) return;

        setIsClearing(true);
        setStatus("");
        try {
            await clearDatabases();
            setMemories([]);
            setEvents([]);
            setStatus("Databases cleared successfully.");
        } catch (error) {
            console.error(error);
            setStatus("Could not clear databases.");
        } finally {
            setIsClearing(false);
        }
    }

    return (
        <div className="dashboard dashboard-simple">
            <div className="dashboard-header-row">
                <div className="dashboard-title">
                    <h1>ATTACKLAYER</h1>
                    <p>Memory Security Overview</p>
                </div>
                <button
                    className="danger-action-btn"
                    onClick={handleClearDatabases}
                    disabled={isClearing}
                >
                    {isClearing ? "Clearing..." : "Clear Databases"}
                </button>
            </div>
            {status && <div className="dashboard-status">{status}</div>}
            <div className="dashboard-metrics">

                <div className="metric-card">
                    <div className="metric-title">
                        Average Trust
                    </div>
                    <div className="metric-value">
                        {averageTrust}
                    </div>
                </div>

                <div className="metric-card">
                    <div className="metric-title">
                        Allowed
                    </div>
                    <div className="metric-value metric-green">
                        {allowedCount}
                    </div>
                </div>

                <div className="metric-card">
                    <div className="metric-title">
                        Blocked
                    </div>
                    <div className="metric-value metric-red">
                        {blockedCount}
                    </div>
                </div>

                <div className="metric-card">
                    <div className="metric-title">
                        Warnings
                    </div>
                    <div className="metric-value metric-orange">
                        {warningCount}
                    </div>
                </div>

            </div>
            <div className="panel">
                <div className="panel-header">
                    <h2>MEMORY VAULT</h2>
                    <button
                        className="excel-download-btn"
                        onClick={() => downloadExcel("memory")}
                    >
                        Download Excel
                    </button>
                </div>
                <MemoryTable memories={memories} />
            </div>

            <div className="panel">
                <div className="panel-header">
                    <h2>RECENT ACTIVITY</h2>
                    <button
                        className="excel-download-btn"
                        onClick={() => downloadExcel("audit")}
                    >
                        Download Excel
                    </button>
                </div>
                <AuditTable events={events.slice(0, 20)} />
            </div>
        </div>
    );
}

export default DashboardPage;
