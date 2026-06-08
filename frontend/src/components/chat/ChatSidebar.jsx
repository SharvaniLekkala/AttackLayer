import { Link } from "react-router-dom";

function ChatSidebar({
    sessions,
    activeId,
    onSelect,
    onNew,
    onDelete
}) {

    return (
        <aside className="chat-sidebar">
            <div className="sidebar-top">
                <button type="button" className="new-chat-btn" onClick={onNew}>
                    + New chat
                </button>
            </div>

            <div className="sidebar-sessions">
                {sessions.length === 0 ? (
                    <p className="sidebar-empty">No chats yet</p>
                ) : (
                    sessions.map((session) => (
                        <div
                            key={session.id}
                            className={
                                session.id === activeId
                                    ? "session-item active"
                                    : "session-item"
                            }
                        >
                            <button
                                type="button"
                                className="session-select"
                                onClick={() => onSelect(session.id)}
                            >
                                {session.title}
                            </button>
                            <button
                                type="button"
                                className="session-delete"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onDelete(session.id);
                                }}
                                title="Delete chat"
                            >
                                ×
                            </button>
                        </div>
                    ))
                )}
            </div>

            <div className="sidebar-footer">
                <Link to="/dashboard" className="sidebar-link">
                    Dashboard
                </Link>
            </div>
        </aside>
    );
}

export default ChatSidebar;
