const STORAGE_KEY = "attacklayer_chat_sessions";

function loadAll() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return [];
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
}

function saveAll(sessions) {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
    } catch (error) {
        console.warn("Could not save chat sessions", error);
    }
}

export function createSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

export function getSessions() {
    return loadAll().sort(
        (a, b) =>
            new Date(b.updatedAt || 0).getTime() -
            new Date(a.updatedAt || 0).getTime()
    );
}

export function getSession(sessionId) {
    return loadAll().find((s) => s.id === sessionId) ?? null;
}

export function createSession() {
    const session = {
        id: createSessionId(),
        title: "New chat",
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };
    const sessions = loadAll();
    sessions.unshift(session);
    saveAll(sessions);
    return session;
}

export function updateSession(sessionId, { messages, title }) {
    const sessions = loadAll();
    const index = sessions.findIndex((s) => s.id === sessionId);
    if (index === -1) return null;

    if (messages !== undefined) {
        sessions[index].messages = messages;
    }
    if (title !== undefined) {
        sessions[index].title = title;
    }
    sessions[index].updatedAt = new Date().toISOString();
    saveAll(sessions);
    return sessions[index];
}

export function deleteSession(sessionId) {
    const sessions = loadAll().filter((s) => s.id !== sessionId);
    saveAll(sessions);
    return sessions;
}

export function titleFromMessage(text) {
    const trimmed = text.trim();
    if (!trimmed) return "New chat";
    return trimmed.length > 32 ? `${trimmed.slice(0, 32)}…` : trimmed;
}

export function bootstrapChatState() {
    try {
        let sessions = getSessions();
        if (sessions.length === 0) {
            const session = createSession();
            sessions = [session];
        }
        const active = sessions[0];
        return {
            sessions,
            activeId: active.id,
            messages: Array.isArray(active.messages) ? active.messages : []
        };
    } catch {
        const session = createSession();
        return {
            sessions: [session],
            activeId: session.id,
            messages: []
        };
    }
}
