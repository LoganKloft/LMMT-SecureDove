import React, { useState, useEffect } from 'react';
import crypto from 'crypto-browserify';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { v4 as uuidv4 } from 'uuid';
import './Room.scss';

const algorithm = 'aes-256-ctr';

const encrypt = async (text, secretKey) => {
    return new Promise((resolve) => {
	const iv = crypto.randomBytes(16);
	const cipher = crypto.createCipheriv(algorithm, secretKey, iv);
	const encrypted = Buffer.concat([cipher.update(text), cipher.final()]);

	resolve({
	    iv: iv.toString('hex'),
	    content: encrypted.toString('base64')
	});
    });
};

const decrypt = async (hash, secretKey) => {
    return new Promise((resolve) => {
	const decipher = crypto.createDecipheriv(
	    algorithm,
	    secretKey,
	    Buffer.from(hash.iv, 'hex')
	);

	const decrypted = Buffer.concat([
	    decipher.update(Buffer.from(hash.content, 'base64')),
	    decipher.final()
	]);

	resolve(decrypted.toString());
    });
};

// when we send a message, we provide the userid which says who is sending the message
// we also need a destination to send the message to, this is the roomid
// the socket is the vessel for communication
export default function Room({ sharedSecretKeys, messages, users, currentRoomId, websocketRef, roomname, username }) {

    const [message, setMessage] = useState("");

    function sendMessageHandler(e) {
        if (websocketRef.current && currentRoomId.current && e.code === "Enter") {
	    for (const user of users) {
		const secretKey = sharedSecretKeys[user];

		if (secretKey == undefined) {
		    console.log(`Can't send message to ${user}! (missing secret key)`);
		    continue;
		}

		(async () => {
		    const encryptedMessage = await encrypt(
			message,
			secretKey.toString('base64')
		    );

		    let request = {
			"type": "message",
			"verb": "post",
			"id": uuidv4(),
			"content": {
			    "roomid": currentRoomId.current,
			    "message": encryptedMessage,
			    "target": user,
			},
		    }

		    websocketRef.current.send(JSON.stringify(request));
		})();
	    }

	    e.target.value = "";
	    setMessage("");
        }
    }

    function handleCopyRoomCode() {
        navigator.clipboard.writeText(currentRoomId.current);
    }

    const [decryptedMessages, setDecryptedMessages] = useState(null);

    useEffect(() => {
	(async () => {
	    Promise.all(messages.map(async (message) => {
		let key = sharedSecretKeys[message.username];
		if (key == undefined)
		    return { "header": message.header, "message": "encrypted message :(" };
		let decrypted = await decrypt(message.message, key.toString('base64'));
		return { "header": message.header, "message": decrypted };
	    })).then(decryptedMessages => {
		setDecryptedMessages(decryptedMessages)
	    });
	})();
    }, [messages, sharedSecretKeys]);

    return (
        <div className="Room">
            <div className="content-wrapper">
                <div className="messages-wrapper">
                    {/* Display messages*/}
                    {
                        decryptedMessages &&
                        decryptedMessages.map(message => {
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
                        { users && users.map(user => <p>{user}</p>) }
                    </div>
                </div>
            </div>

        </div>
    )
}
