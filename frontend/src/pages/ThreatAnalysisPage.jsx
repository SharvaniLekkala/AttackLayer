import { useState, useEffect } from "react";
import {
    getAttackStatistics,
    getAttackTrendOverTime,
    getDecisionDistribution,
    getThreatCategoryDistribution,
    getMemoryUsageDistribution,
    getHumanApprovalVsRejection,
    getAttackSeverityBreakdown,
    getIPIntelligence,
} from "../api/attacklayer";
import "../styles/threat-analysis.css";

/* ===== Helper: Donut Chart (SVG) ===== */
function DonutChart({ segments }) {
    const r = 44;
    const circ = 2 * Math.PI * r;
    const total = segments.reduce((s, x) => s + x.value, 0);
    let offset = 0;

    const arcs = segments.map((seg) => {
        const dash = total > 0 ? (seg.value / total) * circ : 0;
        const arc = {
            dash,
            offset,
            color: seg.color,
            label: seg.label,
            value: seg.value,
        };
        offset += dash;
        return arc;
    });

    return (
        <div className="donut-chart-wrap">
            <svg className="donut-svg" viewBox="0 0 100 100">
                <circle className="donut-bg" cx="50" cy="50" r={r} />
                {total === 0 ? (
                    <circle cx="50" cy="50" r={r} fill="none" stroke="#e2e8f0" strokeWidth="18" />
                ) : (
                    arcs.map((arc, i) => (
                        <circle
                            key={i}
                            className="donut-arc"
                            cx="50"
                            cy="50"
                            r={r}
                            stroke={arc.color}
                            strokeDasharray={`${arc.dash} ${circ - arc.dash}`}
                            strokeDashoffset={-arc.offset}
                        />
                    ))
                )}
            </svg>
            <div className="donut-legend">
                {segments.map((seg, i) => (
                    <div key={i} className="donut-legend-item">
                        <div className="donut-legend-dot" style={{ background: seg.color }} />
                        <span className="donut-legend-label">{seg.label}</span>
                        <span className="donut-legend-value">{seg.value}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

/* ===== Helper: Horizontal Bar Chart ===== */
function BarChart({ items }) {
    if (!items || items.length === 0) {
        return <div className="chart-empty">No data available</div>;
    }
    const maxVal = Math.max(...items.map((x) => x.value), 1);
    return (
        <div className="bar-chart">
            {items.map((item, i) => (
                <div key={i} className="bar-row">
                    <div className="bar-label" title={item.label}>{item.label}</div>
                    <div className="bar-track">
                        <div
                            className={`bar-fill color-${i % 8}`}
                            style={{ width: `${(item.value / maxVal) * 100}%` }}
                        />
                    </div>
                    <div className="bar-value">{item.value}</div>
                </div>
            ))}
        </div>
    );
}

/* ===== Helper: Trend Chart ===== */
function TrendChart({ data }) {
    if (!data || data.length === 0) {
        return <div className="chart-empty">No trend data available</div>;
    }
    const maxVal = Math.max(...data.map((d) => d.count), 1);
    return (
        <div className="trend-chart">
            {data.map((d, i) => (
                <div key={i} className="trend-row">
                    <div className="trend-date">{d.date}</div>
                    <div className="trend-bar-track">
                        <div
                            className="trend-bar-fill"
                            style={{ width: `${(d.count / maxVal) * 100}%` }}
                        />
                    </div>
                    <div className="trend-count">{d.count}</div>
                </div>
            ))}
        </div>
    );
}

/* ===== Helper: Severity Bars (vertical) ===== */
function SeverityChart({ data }) {
    const max = Math.max(
        data.critical || 0, data.high || 0,
        data.medium || 0, data.low || 0, 1
    );
    const barH = (n) => Math.round(((n || 0) / max) * 90);
    return (
        <div style={{ display: "flex", gap: 12 }}>
            <div className="severity-bars">
                {[
                    { key: "critical", label: "CRIT", cls: "critical" },
                    { key: "high", label: "HIGH", cls: "high" },
                    { key: "medium", label: "MED", cls: "medium" },
                    { key: "low", label: "LOW", cls: "low" },
                ].map((s) => (
                    <div key={s.key} className="sev-col">
                        <div className="sev-count">{data[s.key] || 0}</div>
                        <div className={`sev-bar ${s.cls}`} style={{ height: `${barH(data[s.key])}px` }} />
                        <div className="sev-label">{s.label}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}

/* ===== KPI Metadata ===== */
const KPI_META = [
    { key: "totalRequests", label: "Total Requests", icon: "📊" },
    { key: "allowedRequests", label: "Allowed", icon: "✅" },
    { key: "blockedAttacks", label: "Blocked", icon: "🚫" },
    { key: "allowWithWarning", label: "Warnings", icon: "⚠️" },
    { key: "humanApproved", label: "Human Approved", icon: "👍" },
    { key: "humanRejected", label: "Human Rejected", icon: "👎" },
    { key: "promptInjectionAttempts", label: "Prompt Injections", icon: "💉" },
    { key: "memoryPoisoningAttempts", label: "Memory Poisoning", icon: "☣️" },
    { key: "falseFactInjectionAttempts", label: "False Fact Injection", icon: "🎭" },
];

function ThreatAnalysisPage() {
    const [stats, setStats] = useState({});
    const [trend, setTrend] = useState([]);
    const [decisionDist, setDecisionDist] = useState([]);
    const [threatCats, setThreatCats] = useState([]);
    const [memUsage, setMemUsage] = useState({});
    const [humanApproval, setHumanApproval] = useState({});
    const [severity, setSeverity] = useState({});
    const [ipIntel, setIpIntel] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        load();
        const timer = setInterval(load, 10000);
        return () => clearInterval(timer);
    }, []);

    async function load() {
        try {
            const [
                statsData,
                trendData,
                decisionData,
                threatData,
                memData,
                humanData,
                sevData,
                ipData,
            ] = await Promise.all([
                getAttackStatistics(),
                getAttackTrendOverTime(),
                getDecisionDistribution(),
                getThreatCategoryDistribution(),
                getMemoryUsageDistribution(),
                getHumanApprovalVsRejection(),
                getAttackSeverityBreakdown(),
                getIPIntelligence(),
            ]);
            setStats(statsData || {});
            setTrend(trendData || []);
            setDecisionDist(decisionData || []);
            setThreatCats(threatData || []);
            setMemUsage(memData || {});
            setHumanApproval(humanData || {});
            setSeverity(sevData || {});
            setIpIntel(ipData || []);
        } catch (err) {
            console.error("Failed to load threat analysis data", err);
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return (
            <div className="loading-state">
                <div className="spinner" />
                Loading Threat Analysis…
            </div>
        );
    }

    // Prepare decision donut segments
    const decisionSegments = [
        { label: "Allowed", value: stats.allowedRequests || 0, color: "#059669" },
        { label: "Blocked", value: stats.blockedAttacks || 0, color: "#dc2626" },
        { label: "Warning", value: stats.allowWithWarning || 0, color: "#d97706" },
    ];

    // Prepare memory stacked bar
    const memTotal = (memUsage.episodic || 0) + (memUsage.shortTerm || 0) + (memUsage.longTerm || 0) || 1;
    const epPct = Math.round(((memUsage.episodic || 0) / memTotal) * 100);
    const stPct = Math.round(((memUsage.shortTerm || 0) / memTotal) * 100);
    const ltPct = 100 - epPct - stPct;

    const totalHuman = (humanApproval.approved || 0) + (humanApproval.rejected || 0) || 1;

    return (
        <>
            <div className="page-header">
                <h1 className="page-title">Threat Analysis & Security Intelligence</h1>
                <p className="page-subtitle">
                    Comprehensive analytics on detected threats, decisions, and security patterns
                </p>
            </div>

            {/* ===== KPI CARDS ===== */}
            <div className="ta-kpi-grid">
                {KPI_META.map((m) => (
                    <div key={m.key} className="ta-kpi-card">
                        <div className="ta-kpi-icon">{m.icon}</div>
                        <div className="ta-kpi-value">{stats[m.key] ?? 0}</div>
                        <div className="ta-kpi-label">{m.label}</div>
                    </div>
                ))}
            </div>

            {/* ===== CHARTS ===== */}
            <div className="ta-charts-grid">
                {/* Attack Trend */}
                <div className="chart-card">
                    <div className="chart-card-header">
                        <div className="chart-card-title">📈 Attack Trend Over Time</div>
                    </div>
                    <div className="chart-card-body">
                        <TrendChart data={trend} />
                    </div>
                </div>

                {/* Decision Distribution */}
                <div className="chart-card">
                    <div className="chart-card-header">
                        <div className="chart-card-title">🎯 Decision Distribution</div>
                    </div>
                    <div className="chart-card-body">
                        <DonutChart segments={decisionSegments} />
                    </div>
                </div>

                {/* Threat Category */}
                <div className="chart-card">
                    <div className="chart-card-header">
                        <div className="chart-card-title">🔍 Threat Category Distribution</div>
                    </div>
                    <div className="chart-card-body">
                        <BarChart
                            items={(threatCats || []).map((t) => ({
                                label: t.category || t.label || t.threat || "Unknown",
                                value: t.count || t.value || 0,
                            }))}
                        />
                    </div>
                </div>

                {/* Memory Usage */}
                <div className="chart-card">
                    <div className="chart-card-header">
                        <div className="chart-card-title">🧠 Memory Usage Distribution</div>
                    </div>
                    <div className="chart-card-body">
                        <div className="stacked-bar-wrap">
                            <div className="stacked-bar-track">
                                <div className="stacked-segment episodic" style={{ width: `${epPct}%` }}>
                                    {epPct > 10 ? `${epPct}%` : ""}
                                </div>
                                <div className="stacked-segment short-term" style={{ width: `${stPct}%` }}>
                                    {stPct > 10 ? `${stPct}%` : ""}
                                </div>
                                <div className="stacked-segment long-term" style={{ width: `${ltPct}%` }}>
                                    {ltPct > 10 ? `${ltPct}%` : ""}
                                </div>
                            </div>
                            <div className="stacked-legend">
                                <div className="stacked-legend-item">
                                    <div className="stacked-dot" style={{ background: "#3b82f6" }} />
                                    Episodic ({memUsage.episodic || 0})
                                </div>
                                <div className="stacked-legend-item">
                                    <div className="stacked-dot" style={{ background: "#0891b2" }} />
                                    Short-Term ({memUsage.shortTerm || 0})
                                </div>
                                <div className="stacked-legend-item">
                                    <div className="stacked-dot" style={{ background: "#7c3aed" }} />
                                    Long-Term ({memUsage.longTerm || 0})
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Human Approval vs Rejection */}
                <div className="chart-card">
                    <div className="chart-card-header">
                        <div className="chart-card-title">👤 Human Approval vs Rejection</div>
                    </div>
                    <div className="chart-card-body">
                        <div className="comparison-wrap">
                            <div className="comparison-row">
                                <div className="comparison-label-row">
                                    <span className="comparison-label">Approved</span>
                                    <span className="comparison-val">{humanApproval.approved || 0}</span>
                                </div>
                                <div className="comparison-track">
                                    <div
                                        className="comparison-fill approved"
                                        style={{ width: `${((humanApproval.approved || 0) / totalHuman) * 100}%` }}
                                    />
                                </div>
                            </div>
                            <div className="comparison-row">
                                <div className="comparison-label-row">
                                    <span className="comparison-label">Rejected</span>
                                    <span className="comparison-val">{humanApproval.rejected || 0}</span>
                                </div>
                                <div className="comparison-track">
                                    <div
                                        className="comparison-fill rejected"
                                        style={{ width: `${((humanApproval.rejected || 0) / totalHuman) * 100}%` }}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Severity Breakdown */}
                <div className="chart-card">
                    <div className="chart-card-header">
                        <div className="chart-card-title">🔥 Attack Severity Breakdown</div>
                    </div>
                    <div className="chart-card-body">
                        <SeverityChart data={severity} />
                    </div>
                </div>
            </div>

            {/* ===== IP INTELLIGENCE ===== */}
            <div className="ip-intel-section">
                <div className="ip-intel-header">
                    <h2>🌐 IP Intelligence</h2>
                </div>
                <div className="ip-intel-table-wrap">
                    <table className="ip-intel-table">
                        <thead>
                            <tr>
                                <th>Source IP</th>
                                <th>Country</th>
                                <th>Risk Score</th>
                                <th>Reputation</th>
                                <th>Status</th>
                                <th>Attempts</th>
                            </tr>
                        </thead>
                        <tbody>
                            {ipIntel.length > 0 ? (
                                ipIntel.map((ip, i) => {
                                    const risk = ip.riskScore || ip.risk_score || 0;
                                    const riskCls =
                                        risk > 0.7
                                            ? "risk-high"
                                            : risk > 0.4
                                            ? "risk-mid"
                                            : "risk-low";
                                    return (
                                        <tr key={i}>
                                            <td><span className="ip-code">{ip.ipAddress || ip.ip || "—"}</span></td>
                                            <td>{ip.country || "Unknown"}</td>
                                            <td className={`risk-score-cell ${riskCls}`}>
                                                {risk.toFixed(2)}
                                            </td>
                                            <td>{ip.reputation || "—"}</td>
                                            <td>
                                                <span className={ip.status === "BLOCKED" ? "badge badge-block" : "badge badge-allow"}>
                                                    {ip.status || "—"}
                                                </span>
                                            </td>
                                            <td style={{ fontWeight: 600 }}>{ip.attempts || 0}</td>
                                        </tr>
                                    );
                                })
                            ) : (
                                <tr>
                                    <td colSpan={6} style={{ textAlign: "center", color: "var(--color-text-muted)", padding: "32px 16px", fontSize: 13 }}>
                                        No IP intelligence data available
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </>
    );
}

export default ThreatAnalysisPage;