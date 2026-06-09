import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import MemoryTable from "../components/dashboard/MemoryTable";
import AuditTable from "../components/dashboard/AuditTable";
import { getAllMemories, getAuditEvents, downloadCsv } from "../api/attacklayer";
import "../styles/dashboard.css";

function DashboardPage() {

    const [memories, setMemories] = useState([]);
    const [events, setEvents] = useState([]);

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

    return (
        <div className="dashboard dashboard-simple">
            <div className="dashboard-header-row">
                <div className="dashboard-title">
                    <h1>ATTACKLAYER</h1>
                    <p>Memory Security Overview</p>
                </div>
                <Link to="/chat" className="dashboard-chat-link">
                    Open Chat
                </Link>
            </div>

            <div className="panel">
                <div className="panel-header">
                    <h2>MEMORY VAULT</h2>
                    <button
                        className="csv-download-btn"
                        onClick={() => downloadCsv("memory")}
                    >
                        Download CSV
                    </button>
                </div>
                <MemoryTable memories={memories} />
            </div>

            <div className="panel">
                <div className="panel-header">
                    <h2>RECENT ACTIVITY</h2>
                    <button
                        className="csv-download-btn"
                        onClick={() => downloadCsv("audit")}
                    >
                        Download CSV
                    </button>
                </div>
                <AuditTable events={events.slice(0, 20)} />
            </div>
        </div>
    );
}

export default DashboardPage;
