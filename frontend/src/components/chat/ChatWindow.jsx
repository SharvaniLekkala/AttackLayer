import MessageBubble from "./MessageBubble";

function ChatWindow({

    messages

}) {

    return (

        <div className="chat-window">

            {

                messages.map(

                    (

                        message,

                        index

                    ) => (

                        <MessageBubble

                            key={index}

                            sender={message.sender}

                            text={message.text}

                        />

                    )

                )

            }

        </div>

    );

}

export default ChatWindow;