import { useState, useEffect } from "react";
import {
    getAllMemories,
    clearEpisodicMemory,
    clearShortTermMemory,
    clearLongTermMemory,
} from "../api/attacklayer";
import "../styles/memory-vault.css";

function MemoryItem({ mem }) {
    const trust = mem.trust_score || 0;
    const trustClass =
        trust >= 0.7 ? "trust-high" : trust >= 0.4 ? "trust-mid" : "trust-low";
    return (
        <div className="memory-item">
            <div className="memory-item-fact">{mem.fact || "—"}</div>
            <div className="memory-item-meta">
                <span className={`memory-meta-chip ${trustClass}`}>
                    Trust: {trust.toFixed(2)}
                </span>
                {mem.category && (
                    <span className="memory-meta-chip">
                        {mem.category}
                    </span>
                )}
                {mem.source && (
                    <span className="memory-meta-chip">
                        {mem.source}
                    </span>
                )}
                <span className="memory-meta-chip">
                    {new Date(mem.updated_at || mem.created_at || Date.now()).toLocaleDateString()}
                </span>
            </div>
        </div>
    );
}

function MemoryPanel({ type, title, desc, memories, onClear, accentClass, icon }) {
    const [confirming, setConfirming] = useState(false);
    const [clearing, setClearing] = useState(false);

    async function doConfirmClear() {
        setClearing(true);
        await onClear();
        setConfirming(false);
        setClearing(false);
    }

    return (
        <>
            <div className={`memory-panel ${accentClass}`}>
                {/* Header */}
                <div className="memory-panel-header">
                    <div className="panel-title-row">
                        <div className="panel-title">
                            {icon}
                            {title}
                        </div>
                        <span className="panel-count-badge">{memories.length}</span>
                    </div>
                    <div className="panel-desc">{desc}</div>
                </div>

                {/* Body */}
                <div className="memory-panel-body">
                    {memories.length === 0 ? (
                        <div className="panel-empty">
                            <div className="panel-empty-icon">📭</div>
                            <p>No {title.toLowerCase()} stored</p>
                        </div>
                    ) : (
                        memories.map((mem, i) => (
                            <MemoryItem key={mem.id || i} mem={mem} />
                        ))
                    )}
                </div>

                {/* Footer */}
                <div className="memory-panel-footer">
                    <span className="panel-footer-info">
                        {memories.length} {memories.length === 1 ? "entry" : "entries"}
                    </span>
                    <button
                        className="clear-btn"
                        disabled={memories.length === 0}
                        onClick={() => setConfirming(true)}
                    >
                        <svg viewBox="0 0 24 24">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6l-1 14H6L5 6"/>
                            <path d="M10 11v6M14 11v6"/>
                        </svg>
                        Clear {title}
                    </button>
                </div>
            </div>

            {/* Confirm dialog */}
            {confirming && (
                <div className="confirm-overlay" onClick={() => setConfirming(false)}>
                    <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
                        <h3>Clear {title}?</h3>
                        <p>
                            This will permanently delete all {memories.length}{" "}
                            {title.toLowerCase()} entries. This action cannot be undone.
                        </p>
                        <div className="confirm-actions">
                            <button className="confirm-cancel-btn" onClick={() => setConfirming(false)}>
                                Cancel
                            </button>
                            <button
                                className="confirm-clear-btn"
                                onClick={doConfirmClear}
                                disabled={clearing}
                            >
                                {clearing ? "Clearing…" : "Yes, Clear"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}

function MemoryVaultPage() {
    const [episodic, setEpisodic] = useState(() => {
        try { return JSON.parse(localStorage.getItem("attacklayer_mem_episodic") || "[]"); } catch { return []; }
    });
    const [shortTerm, setShortTerm] = useState(() => {
        try { return JSON.parse(localStorage.getItem("attacklayer_mem_shortterm") || "[]"); } catch { return []; }
    });
    const [longTerm, setLongTerm] = useState(() => {
        try { return JSON.parse(localStorage.getItem("attacklayer_mem_longterm") || "[]"); } catch { return []; }
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        load();
        const timer = setInterval(load, 8000);
        return () => clearInterval(timer);
    }, []);

    async function load() {
        try {
            const all = await getAllMemories();
            const ep = all.filter(
                (m) =>
                    m.memory_type === "EPISODIC" ||
                    (
                        m.source &&
                        m.source.toLowerCase().includes("session")
                    )
            );
            const st = all.filter(
                (m) =>
                    m.memory_type === "SHORT_TERM" ||
                    (
                        m.importance_score != null &&
                        m.importance_score < 0.5 &&
                        !ep.includes(m)
                    )
            );
            const lt = all.filter(
                (m) =>
                    m.memory_type === "LONG_TERM" ||
                    (
                        m.trust_score > 0.7 &&
                        m.importance_score >= 0.5 &&
                        !ep.includes(m) &&
                        !st.includes(m)
                    )
            );

            let finalEp, finalSt, finalLt;
            if (ep.length === 0 && st.length === 0 && lt.length === 0 && all.length > 0) {
                const t = Math.ceil(all.length / 3);
                finalEp = all.slice(0, t);
                finalSt = all.slice(t, 2 * t);
                finalLt = all.slice(2 * t);
            } else {
                finalEp = ep; finalSt = st; finalLt = lt;
            }
            setEpisodic(finalEp);
            setShortTerm(finalSt);
            setLongTerm(finalLt);
            localStorage.setItem("attacklayer_mem_episodic", JSON.stringify(finalEp));
            localStorage.setItem("attacklayer_mem_shortterm", JSON.stringify(finalSt));
            localStorage.setItem("attacklayer_mem_longterm", JSON.stringify(finalLt));
            setError("");
        } catch {
            // Backend down — cached data already in state, don't overwrite
            const hasCached = localStorage.getItem("attacklayer_mem_episodic");
            if (!hasCached) setError("Failed to load memories.");
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return (
            <div className="loading-state">
                <div className="spinner" />
                Loading Memory Vault…
            </div>
        );
    }

    return (
        <>
            <div className="page-header">
                <h1 className="page-title">Memory Vault</h1>
                <p className="page-subtitle">
                    Manage and monitor the AI agent's memory systems — episodic, short-term, and long-term storage
                </p>
            </div>

            {error && (
                <div style={{ marginBottom: 20, padding: "12px 16px", background: "var(--color-danger-bg)", border: "1px solid var(--color-danger-border)", borderRadius: "var(--radius-md)", color: "var(--color-danger)", fontSize: 13 }}>
                    {error}
                </div>
            )}

            <div className="memory-panels">
                <MemoryPanel
                    type="episodic"
                    accentClass="episodic"
                    title="Episodic Memory"
                    desc="Session-specific memories · Temporary context"
                    memories={episodic}
                    onClear={async () => {
                        try { await clearEpisodicMemory(); setEpisodic([]); } catch { setError("Failed to clear episodic memory."); }
                    }}
                    icon={
                        <svg viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10"/>
                            <polyline points="12 6 12 12 16 14"/>
                        </svg>
                    }
                />
                <MemoryPanel
                    type="short-term"
                    accentClass="short-term"
                    title="Short-Term Memory"
                    desc="Recent interactions · Active conversation memory"
                    memories={shortTerm}
                    onClear={async () => {
                        try { await clearShortTermMemory(); setShortTerm([]); } catch { setError("Failed to clear short-term memory."); }
                    }}
                    icon={
                        <svg viewBox="0 0 24 24">
                            <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
                        </svg>
                    }
                />
                <MemoryPanel
                    type="long-term"
                    accentClass="long-term"
                    title="Long-Term Memory"
                    desc="Persistent knowledge · Stored trusted information"
                    memories={longTerm}
                    onClear={async () => {
                        try { await clearLongTermMemory(); setLongTerm([]); } catch { setError("Failed to clear long-term memory."); }
                    }}
                    icon={
                        <svg viewBox="0 0 24 24">
                            <ellipse cx="12" cy="5" rx="9" ry="3"/>
                            <path d="M3 5v14a9 3 0 0018 0V5"/>
                            <path d="M3 12a9 3 0 0018 0"/>
                        </svg>
                    }
                />
            </div>
        </>
    );
}

export default MemoryVaultPage;