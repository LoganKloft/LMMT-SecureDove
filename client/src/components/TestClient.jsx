import React from 'react'
import { GlobalCryptoState } from './CryptoState';
import { v4 as uuidv4 } from 'uuid';
import fernet from 'fernet';
import { useNavigate } from 'react-router-dom';
import { Snackbar } from './Snackbar';

function TestClient({ websocketRef }) {

    const navigate = useNavigate();

    function sendUnencryptedMessage() {
        if (websocketRef.current) {
            let request = {
                "type": "none",
                "verb": "none",
                "id": uuidv4(),
                "content": {
                    "none": "none"
                }
            }

            websocketRef.current.send(JSON.stringify(request));

            Snackbar.success("Sent! Check the server to see whether it crashed!");
        }
    }

    function sendEncryptedMessage() {
        if (websocketRef.current) {
            let symmetric = GlobalCryptoState.getSymmetric();
            console.log(symmetric.length);
            let secret = new fernet.Secret(symmetric);
            let token = new fernet.Token({
                secret: secret,
            })

            let content = { "HAHA": "I AM NOT WHAT YOU EXPECTED" };
            content = JSON.stringify(content);
            content = token.encode(content);

            console.log(content);

            let request = {
                "type": "room",
                "verb": "post",
                "id": uuidv4(),
                "content": content
            }

            websocketRef.current.send(JSON.stringify(request));

            Snackbar.success("Sent! Check the server to see whether it crashed!");
        }
    }
    return (
        <div>
            <h1 style={{ "textAlign": "center" }}>Test sending a message that is unencrypted</h1>
            <button onClick={() => sendUnencryptedMessage()}>
                Send
            </button>
            <h1 style={{ "textAlign": "center" }}>Test sending a message that is encrypted but not in expected format</h1>
            <button onClick={() => sendEncryptedMessage()}>
                Send
            </button>
            <h1 style={{ "textAlign": "center" }}>Go back to the home page</h1>
            <button onClick={() => navigate('/home')}>Home</button>
        </div>
    )
}

export default TestClient