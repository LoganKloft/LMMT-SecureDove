import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import './Room.scss';

// when we send a message, we provide the userid which says who is sending the message
// we also need a destination to send the message to, this is the roomid
// the socket is the vessel for communication
export default function Room({ messages, users, currentRoomId, websocketRef }) {

    const [message, setMessage] = useState("");

    function sendMessageHandler(e) {
        if (websocketRef.current && currentRoomId.current && e.code === "Enter") {
            console.log("success");
            let request = {
                "type": "message",
                "verb": "post",
                "content": {
                    "roomid": currentRoomId.current,
                    "message": message
                },
            }

            websocketRef.current.send(JSON.stringify(request));

            e.target.value = "";
            setMessage("");
        }
    }

    return (
        <div className="Room">
            <div className="content-wrapper">
                <div className="messages-wrapper">
                    {/* Display messages*/}
                    {
                        messages &&
                        messages.map(message => {
                            return (
                                <div className="message">
                                    <p className="messageHeader">{message.header}</p>
                                    <p className="messageContent">{message.message}</p>
                                </div>
                            )
                        })
                    }
                </div>

                <div className="input-wrapper">
                    {/* Input for message */}
                    <TextField onKeyUp={sendMessageHandler} onChange={(event) => {
                        setMessage(event.target.value);
                    }} id="standard-basic" label="Enter message" variant="standard" fullWidth />
                </div>
            </div>

            <div className="participants-wrapper">
                <div>
                    {/* participants */}
                    <div>
                        {
                            users &&
                            users.map(user => {
                                return (<p>{user}</p>)
                            })
                        }
                    </div>
                </div>
            </div>

        </div>
    )
}
