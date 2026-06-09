import axios from "axios";

const API = axios.create({
    baseURL: "http://localhost:8000"
});

export async function sendChatMessage(userId, message) {
    const response = await API.post("/chat/", null, {
        params: { user_id: userId, message: message }
    });
    return response.data;
}

export async function getAuditEvents() {
    const response = await API.get("/audit/events");
    return response.data;
}

export async function getAllMemories() {
    const response = await API.get("/memory/all");
    return response.data;
}

export function downloadCsv(exportType) {
    const urls = {
        audit: "/export/audit-csv",
        memory: "/export/memory-csv",
        history: "/export/history-csv",
    };
    const url = `http://localhost:8000${urls[exportType]}`;
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
