import {

    useState

} from "react";

import {

    sendChatMessage

} from "../api/attacklayer";

import "../styles/chat.css";

function ChatPage(){

    const [

        messages,

        setMessages

    ]=useState([

        {

            role:

            "assistant",

            content:

            "Hello! How can I help you today?"

        }

    ]);

    const [

        input,

        setInput

    ]=useState("");

    async function send(){

        if(

            !input.trim()

        ){

            return;

        }

        const userMessage={

            role:

            "user",

            content:

            input

        };

        setMessages(

            previous=>

            [

                ...previous,

                userMessage

            ]

        );

        const current=input;

        setInput("");

        try{

            const response=

            await sendChatMessage(

                1,

                current

            );

            setMessages(

                previous=>

                [

                    ...previous,

                    {

                        role:

                        "assistant",

                        content:

                        response.response

                    }

                ]

            );

        }

        catch(

            error

        ){

            setMessages(

                previous=>

                [

                    ...previous,

                    {

                        role:

                        "assistant",

                        content:

                        "Sorry, something went wrong."

                    }

                ]

            );

        }

    }

    return(

        <div

            className=

            "chat-page"

        >

            <div

                className=

                "chat-container"

            >

                <div

                    className=

                    "chat-header"

                >

                    <h1>

                        AI Assistant

                    </h1>

                </div>

                <div

                    className=

                    "chat-messages"

                >

                    {

                        messages.map(

                            (

                                message,

                                index

                            )=>

                            (

                                <div

                                    key={

                                        index

                                    }

                                    className={

                                        message.role===

                                        "user"

                                        ?

                                        "user-message"

                                        :

                                        "assistant-message"

                                    }

                                >

                                    {

                                        message.content

                                    }

                                </div>

                            )

                        )

                    }

                </div>

                <div

                    className=

                    "chat-input"

                >

                    <input

                        value={

                            input

                        }

                        onChange={

                            event=>

                            setInput(

                                event.target.value

                            )

                        }

                        placeholder=

                        "Message AI Assistant..."

                        onKeyDown={

                            event=>{

                                if(

                                    event.key===

                                    "Enter"

                                ){

                                    send();

                                }

                            }

                        }

                    />

                    <button

                        onClick={

                            send

                        }

                    >

                        Send

                    </button>

                </div>

            </div>

        </div>

    );

}

export default ChatPage;