import { useState, useRef, useEffect } from "react";
import { sendChatMessage } from "../api/attacklayer";
import MessageBubble from "../components/chat/MessageBubble";
import ChatSidebar from "../components/chat/ChatSidebar";
import {
    getSessions,
    createSession,
    getSession,
    updateSession,
    deleteSession,
    titleFromMessage,
    bootstrapChatState
} from "../utils/chatSessions";
import "../styles/chat.css";

function ChatPage() {

    const initial = bootstrapChatState();

    const [sessions, setSessions] = useState(initial.sessions);
    const [activeId, setActiveId] = useState(initial.activeId);
    const [messages, setMessages] = useState(initial.messages);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);

    function refreshSessions() {
        setSessions(getSessions());
    }

    function selectSession(sessionId) {
        const session = getSession(sessionId);
        if (!session) return;
        setActiveId(sessionId);
        setMessages(Array.isArray(session.messages) ? session.messages : []);
    }

    function handleNewChat() {
        const session = createSession();
        refreshSessions();
        setActiveId(session.id);
        setMessages([]);
        setInput("");
    }

    function handleDelete(sessionId) {
        const remaining = deleteSession(sessionId);
        refreshSessions();

        if (sessionId !== activeId) return;

        if (remaining.length > 0) {
            selectSession(remaining[0].id);
            return;
        }

        const session = createSession();
        refreshSessions();
        setActiveId(session.id);
        setMessages([]);
    }

    function persistMessages(sessionId, nextMessages, title) {
        updateSession(sessionId, {
            messages: nextMessages,
            ...(title ? { title } : {})
        });
        refreshSessions();
    }

    async function send() {
        if (!input.trim() || loading || !activeId) return;

        const userMessage = { role: "user", content: input };
        const nextMessages = [...messages, userMessage];

        setMessages(nextMessages);

        const isFirstMessage = messages.length === 0;
        const title = isFirstMessage ? titleFromMessage(input) : undefined;

        persistMessages(activeId, nextMessages, title);

        const current = input;
        setInput("");
        setLoading(true);

        try {
            const response = await sendChatMessage(activeId, current);
            const withReply = [
                ...nextMessages,
                { role: "assistant", content: response.response }
            ];
            setMessages(withReply);
            persistMessages(activeId, withReply);
        } catch {
            const withError = [
                ...nextMessages,
                {
                    role: "assistant",
                    content: "Sorry, something went wrong. Please try again."
                }
            ];
            setMessages(withError);
            persistMessages(activeId, withError);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="chat-layout">
            <ChatSidebar
                sessions={sessions}
                activeId={activeId}
                onSelect={selectSession}
                onNew={handleNewChat}
                onDelete={handleDelete}
            />

            <div className="chat-main">
                <div className="chat-messages">
                    {messages.length === 0 && !loading && (
                        <div className="chat-welcome">
                            <h2>How can I help you today?</h2>
                        </div>
                    )}
                    {messages.map((message, index) => (
                        <MessageBubble
                            key={index}
                            sender={message.role === "user" ? "user" : "assistant"}
                            text={message.content}
                        />
                    ))}
                    {loading && (
                        <div className="chat-loading">
                            <span className="typing-dot" />
                            <span className="typing-dot" />
                            <span className="typing-dot" />
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-area">
                    <div className="chat-input">
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Message..."
                            onKeyDown={(e) => {
                                if (e.key === "Enter" && !e.shiftKey) {
                                    e.preventDefault();
                                    send();
                                }
                            }}
                            disabled={loading}
                        />
                        <button
                            type="button"
                            onClick={send}
                            disabled={loading || !input.trim()}
                        >
                            Send
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ChatPage;
