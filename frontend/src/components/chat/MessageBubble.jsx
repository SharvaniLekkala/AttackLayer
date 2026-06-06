function MessageBubble({

    sender,

    text

}) {

    return (

        <div
            className={
                sender === "user"
                ?
                "message-row user-row"
                :
                "message-row ai-row"
            }
        >

            <div
                className={
                    sender === "user"
                    ?
                    "message-bubble user-bubble"
                    :
                    "message-bubble ai-bubble"
                }
            >

                {text}

            </div>

        </div>

    );

}

export default MessageBubble;