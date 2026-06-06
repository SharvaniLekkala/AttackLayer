import {

    useState

} from "react";

function ChatInput({

    onSend

}) {

    const [

        input,

        setInput

    ] = useState("");

    function handleSend() {

        if (

            input.trim()

            ===

            ""

        ) {

            return;

        }

        onSend(

            input

        );

        setInput(

            ""

        );

    }

    return (

        <div

            className="chat-input"

        >

            <input

                type="text"

                placeholder="Type your message..."

                value={

                    input

                }

                onChange={

                    (

                        e

                    ) =>

                        setInput(

                            e.target.value

                        )

                }

            />

            <button

                onClick={

                    handleSend

                }

            >

                Send

            </button>

        </div>

    );

}

export default ChatInput;