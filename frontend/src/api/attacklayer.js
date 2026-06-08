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
