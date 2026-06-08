function MessageBubble({ sender, text }) {

    return (
        <div
            className={
                sender === "user"
                    ? "message-block user-block"
                    : "message-block assistant-block"
            }
        >
            <div
                className={
                    sender === "user"
                        ? "message-bubble user-bubble"
                        : "message-bubble assistant-bubble"
                }
            >
                {text}
            </div>
        </div>
    );
}

export default MessageBubble;
