import React, { useEffect, useState } from 'react'
import InputLabel from '@mui/material/InputLabel';
import InputAdornment from '@mui/material/InputAdornment';
import FormControl from '@mui/material/FormControl';
import AccountCircle from '@mui/icons-material/AccountCircle';
import Stack from '@mui/material/Stack';
import { v4 as uuidv4 } from 'uuid';
import { Snackbar } from './Snackbar';
import { useNavigate } from 'react-router-dom';
import { GlobalCryptoState } from './CryptoState';
import './Login.scss'
import { TextField } from '@mui/material';

export default function Login({ websocketRef }) {

    const [username, setUsername] = useState("");
    const [error, setError] = useState(false);

    const navigate = useNavigate();

    useEffect(() => {
        websocketRef.current = new WebSocket("ws://localhost:8001/");

        websocketRef.current.addEventListener("open", async () => {

            Snackbar.success("Websocket connection opened!");

            let keyPair = await window.crypto.subtle.generateKey(
                {
                    name: "RSA-OAEP",
                    modulusLength: 4096,
                    publicExponent: new Uint8Array([1, 0, 1]),
                    hash: "SHA-256",
                },
                true,
                ["encrypt", "decrypt"],
            );

            GlobalCryptoState.setKeyPair(keyPair);
        })

        websocketRef.current.addEventListener("message", async ({ data }) => {
            const response = JSON.parse(data);

            if (response["type"] === "profile") {
                if (response["verb"] === "post") {
                    if (response["content"]["status"] === true) {
                        GlobalCryptoState.setSymmetric(response["content"]["symmetric"]);
                        console.log(response);

                        // go to home
                        navigate('/home');
                    }
                    else {
                        setError(true);
                    }
                }
            }
        })

        websocketRef.current.addEventListener("close", () => {
            Snackbar.error("WebSocket connection closed!")
        })
    }, [])

    async function buttonClickHandler() {
        if (!username) {
            setError(true);
            return null;
        }


        const exported = await window.crypto.subtle.exportKey("spki", GlobalCryptoState.getKeyPair().publicKey);
        const exportedAsString = String.fromCharCode.apply(null, new Uint8Array(exported));
        const exportedAsBase64 = window.btoa(exportedAsString);
        const pemExported = `-----BEGIN PUBLIC KEY-----\n${exportedAsBase64}\n-----END PUBLIC KEY-----`;

        const exportedPr = await window.crypto.subtle.exportKey("pkcs8", GlobalCryptoState.getKeyPair().privateKey);
        const exportedAsStringPr = String.fromCharCode.apply(null, new Uint8Array(exportedPr));
        const exportedAsBase64Pr = window.btoa(exportedAsStringPr);
        const pemExportedPr = `-----BEGIN PRIVATE KEY-----\n${exportedAsBase64Pr}\n-----END PRIVATE KEY-----`;

        let request = {
            "type": "profile",
            "verb": "post",
            "id": uuidv4(),
            "content": {
                "username": username,
                "public": pemExported
            }
        };

        websocketRef.current.send(JSON.stringify(request));
    }

    return (
        <div className="Login background">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <Stack direction="column" spacing={2}>
                <FormControl variant="standard">
                    <InputLabel htmlFor="username" />
                    <TextField
                        id="username"
                        required
                        label="Username"
                        value={username}
                        error={!!error}
                        variant="standard"
                        InputProps={{
                            startAdornment:
                                <InputAdornment position="start">
                                    <AccountCircle />
                                </InputAdornment>
                        }}
                        onChange={(event) => {
                            setUsername(event.target.value);
                        }}
                        helperText={error ? 'Username is required' : ''}
                    />
                </FormControl>
                <button className="submit" onClick={buttonClickHandler}>Login</button>
            </Stack>
        </div>
    )
}
