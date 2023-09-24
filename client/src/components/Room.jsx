import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import './Room.scss';

// when we send a message, we provide the userid which says who is sending the message
// we also need a destination to send the message to, this is the roomid
// the socket is the vessel for communication
export default function Room({ userid, username, roomid, socket }) {

    const [messages, setMessages] = useState([{ "header": "Logan @ 9/24/2023 11:25", "message": "Hello World!" }]);
    const [users, setUsers] = useState(["Logan"]);

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
                    <TextField id="standard-basic" label="Enter message" variant="standard" fullWidth />
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
