function MemoryTable({ memories }) {

    function getStatusColor(status) {
        if (status === "ACTIVE") {
            return "#22c55e";
        }
        return "#ef4444";
    }

    function getAttackColor(attackType) {
        if (!attackType || attackType === "NONE") {
            return "#94a3b8";
        }
        return "#ef4444";
    }

    return (
        <div className="dashboard-table-wrap">
        <table className="dashboard-table memory-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Memory</th>
                    <th>Category</th>
                    <th>Trust</th>
                    <th>Poison</th>
                    <th>Attack</th>
                    <th>Version</th>
                    <th>Conflicts</th>
                    <th>Status</th>
                    <th>Source</th>
                </tr>
            </thead>
            <tbody>
                {memories.length === 0 ? (
                    <tr>
                        <td colSpan="10">No memories</td>
                    </tr>
                ) : (
                    memories.map((memory) => (
                        <tr key={memory.id}>
                            <td>{memory.id}</td>
                            <td>{memory.fact}</td>
                            <td>{memory.category}</td>
                            <td>{memory.trust_score}</td>
                            <td>{memory.poison_score}</td>
                            <td
                                style={{
                                    color: getAttackColor(memory.attack_type),
                                    fontWeight: "bold"
                                }}
                            >
                                {memory.attack_type ?? "NONE"}
                            </td>
                            <td>{memory.memory_version ?? memory.version ?? 1}</td>
                            <td>{memory.conflict_count ?? 0}</td>
                            <td
                                style={{
                                    color: getStatusColor(memory.status),
                                    fontWeight: "bold"
                                }}
                            >
                                {memory.status}
                            </td>
                            <td>{memory.source}</td>
                        </tr>
                    ))
                )}
            </tbody>
        </table>
        </div>
    );
}

export default MemoryTable;
