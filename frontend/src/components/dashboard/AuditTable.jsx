function AuditTable({ events }) {

    function getDecisionColor(decision) {
        if (decision === "BLOCK") {
            return "#ef4444";
        }
        if (decision === "REVIEW" || decision === "ALLOW_WITH_WARNING") {
            return "#f59e0b";
        }
        return "#22c55e";
    }

    function getThreatColor(threat) {
        if (!threat || threat === "NONE" || threat === "SAFE") {
            return "#22c55e";
        }
        return "#ef4444";
    }

    return (
        <table className="dashboard-table">
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Prompt</th>
                    <th>Intent</th>
                    <th>Operation</th>
                    <th>Attack</th>
                    <th>Risk</th>
                    <th>Threat</th>
                    <th>Resp Conf</th>
                    <th>Exec (ms)</th>
                    <th>Decision</th>
                </tr>
            </thead>
            <tbody>
                {events.length === 0 ? (
                    <tr>
                        <td colSpan="10">No activity</td>
                    </tr>
                ) : (
                    events.map((event, index) => (
                        <tr key={index}>
                            <td>{event.time}</td>
                            <td>{event.prompt}</td>
                            <td>
                                {event.intent ?? "—"}
                                {event.intent_confidence != null && (
                                    <span> ({event.intent_confidence})</span>
                                )}
                            </td>
                            <td>{event.operation}</td>
                            <td
                                style={{
                                    color: getThreatColor(event.attack_type),
                                    fontWeight: "bold"
                                }}
                            >
                                {event.attack_type ?? "SAFE"}
                                {event.attack_confidence != null && (
                                    <span> ({event.attack_confidence})</span>
                                )}
                            </td>
                            <td>{event.risk_level ?? event.risk_score}</td>
                            <td
                                style={{
                                    color: getThreatColor(event.threat),
                                    fontWeight: "bold"
                                }}
                            >
                                {event.threat}
                            </td>
                            <td>{event.response_confidence ?? "—"}</td>
                            <td>{event.execution_time_ms ?? "—"}</td>
                            <td
                                style={{
                                    color: getDecisionColor(
                                        event.final_decision ?? event.decision
                                    ),
                                    fontWeight: "bold"
                                }}
                            >
                                {event.final_decision ?? event.decision}
                            </td>
                        </tr>
                    ))
                )}
            </tbody>
        </table>
    );
}

export default AuditTable;
