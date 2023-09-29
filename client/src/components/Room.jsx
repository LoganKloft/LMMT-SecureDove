import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { v4 as uuidv4 } from 'uuid';
import './Room.scss';

// when we send a message, we provide the userid which says who is sending the message
// we also need a destination to send the message to, this is the roomid
// the socket is the vessel for communication
export default function Room({ messages, users, currentRoomId, websocketRef, roomname }) {

    const [message, setMessage] = useState("");

    function sendMessageHandler(e) {
        if (websocketRef.current && currentRoomId.current && e.code === "Enter") {
            let request = {
                "type": "message",
                "verb": "post",
                "id": uuidv4(),
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

    function handleCopyRoomCode() {
        navigator.clipboard.writeText(currentRoomId.current);
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
                    {
                        currentRoomId.current &&
                        <Tooltip title="Copy room code">
                            <IconButton onClick={handleCopyRoomCode}>
                                <ContentCopyIcon />
                            </IconButton>
                        </Tooltip>
                    }
                </div>
            </div>

            <div className="participants-wrapper">
                <div>
                    {/* roomname */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '5px', color: 'black', fontFamily: 'Arial, Helvetica, sans-serif', fontSize: '30px', fontWeight: 'bold' }}><p>{roomname}</p></div>

                    {/* participants */}
                    <div style={{ display: 'flex', alignItems: 'left', justifyContent: 'left', color: 'black', flexDirection: 'column', fontSize: '20px' }}>
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
