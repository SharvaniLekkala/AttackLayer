import axios from "axios";

const API = axios.create({
    baseURL: "http://localhost:8000",
});

/* ===== CHAT ===== */
export async function sendChatMessage(userId, message) {
    const response = await API.post("/chat/", null, {
        params: { user_id: userId || "default", message },
    });
    return response.data;
}

/* ===== AUDIT ===== */
export async function getAuditEvents() {
    const response = await API.get("/audit/events");
    return response.data;
}

/* ===== HITL ===== */
export async function getHitlQueue() {
    const response = await API.get("/hitl/queue");
    return response.data;
}
export async function getResolvedHitlItems() {
    const response = await API.get("/hitl/resolved");
    return response.data;
}
export async function approveHitlRequest(requestId) {
    const response = await API.post(`/hitl/approve/${requestId}`);
    return response.data;
}

export async function rejectHitlRequest(requestId) {
    const response = await API.post(`/hitl/reject/${requestId}`);
    return response.data;
}

/* ===== MEMORY ===== */
export async function getAllMemories() {
    const response = await API.get("/memory/all");
    return response.data;
}

export async function clearEpisodicMemory() {
    const response = await API.delete("/memory/episodic");
    return response.data;
}

export async function clearShortTermMemory() {
    const response = await API.delete("/memory/short-term");
    return response.data;
}

export async function clearLongTermMemory() {
    const response = await API.delete("/memory/long-term");
    return response.data;
}
export const getHitlStatus = async (requestId) => {
    const response = await API.get(
        `/hitl/status/${requestId}`
    );
    return response.data;
};
/* ===== ATTACK STATISTICS ===== */
export async function getAttackStatistics() {
    const response = await API.get("/audit/attack-statistics");
    const raw = response.data;

    // Normalize backend shape to frontend expectations
    return {
        totalRequests:
            (raw.general_chat || 0) + (raw.memory_reads || 0) + (raw.memory_writes || 0) + (raw.blocked || 0),
        allowedRequests:
            raw.allowed ||
            (raw.general_chat || 0) + (raw.memory_reads || 0) + (raw.memory_writes || 0),
        blockedAttacks: raw.blocked || 0,
        allowWithWarning: raw.allow_with_warning || 0,
        humanApproved: raw.human_approved || 0,
        humanRejected: raw.human_rejected || 0,
        promptInjectionAttempts: raw.prompt_injections || 0,
        memoryPoisoningAttempts: raw.memory_poisoning || 0,
        falseFactInjectionAttempts: raw.false_fact_injections || 0,
    };
}

/* ===== THREAT ANALYSIS ENDPOINTS ===== */
export async function getAttackTrendOverTime() {
    try {
        const response = await API.get("/audit/attack-trend-over-time");
        return response.data;
    } catch {
        return [];
    }
}

export async function getDecisionDistribution() {
    try {
        const response = await API.get("/audit/decision-distribution");
        return response.data;
    } catch {
        return [];
    }
}

export async function getThreatCategoryDistribution() {
    try {
        const response = await API.get("/audit/threat-category-distribution");
        return response.data;
    } catch {
        return [];
    }
}

export async function getMemoryUsageDistribution() {
    try {
        const response = await API.get("/audit/memory-usage-distribution");
        return response.data;
    } catch {
        return { episodic: 0, shortTerm: 0, longTerm: 0 };
    }
}

export async function getHumanApprovalVsRejection() {
    try {
        const response = await API.get("/audit/human-approval-vs-rejection");
        return response.data;
    } catch {
        return { approved: 0, rejected: 0 };
    }
}

export async function getAttackSeverityBreakdown() {
    try {
        const response = await API.get("/audit/attack-severity-breakdown");
        return response.data;
    } catch {
        return { critical: 0, high: 0, medium: 0, low: 0 };
    }
}

export async function getIPIntelligence() {
    try {
        const response = await API.get("/audit/ip-intelligence");
        return response.data;
    } catch {
        return [];
    }
}

/* ===== EXISTING ENDPOINTS ===== */
export async function getTopAttackTypes() {
    const response = await API.get("/audit/top-attacks");
    return response.data;
}

export async function getRiskDistribution() {
    const response = await API.get("/audit/risk-distribution");
    return response.data;
}

export async function getTrustBreakdown() {
    const response = await API.get("/audit/trust-breakdown");
    return response.data;
}

export async function getPropagationAnalytics() {
    const response = await API.get("/audit/propagation-analytics");
    return response.data;
}

export function downloadExcel(exportType) {
    const urls = {
        audit: "/export/audit-excel",
        memory: "/export/memory-excel",
        history: "/export/history-excel",
    };
    const url = `http://localhost:8000${urls[exportType]}`;
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

export async function clearDatabases() {
    const response = await API.delete("/admin/databases");
    return response.data;
}