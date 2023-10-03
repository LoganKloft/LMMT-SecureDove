import React, { useState } from 'react'
import Input from '@mui/material/Input';
import InputLabel from '@mui/material/InputLabel';
import InputAdornment from '@mui/material/InputAdornment';
import FormControl from '@mui/material/FormControl';
import AccountCircle from '@mui/icons-material/AccountCircle';
import Stack from '@mui/material/Stack';
import { v4 as uuidv4 } from 'uuid';
import { Snackbar } from './Snackbar';
import { useNavigate } from 'react-router-dom';
import './Login.scss'

export default function Login({ username, setUsername, websocketRef }) {

    const navigate = useNavigate();

    function buttonClickHandler() {
        // attempt to create a websocket
        websocketRef.current = new WebSocket("ws://localhost:8001/");

        // send create profile request when open
        websocketRef.current.addEventListener("open", () => {

            Snackbar.success("Websocket connection opened!");

            let request = {
                "type": "profile",
                "verb": "post",
                "id": uuidv4(),
                "content": {
                    "username": username
                }
            };

            websocketRef.current.send(JSON.stringify(request));
        })

        websocketRef.current.addEventListener("close", () => {
            Snackbar.error("WebSocket connection closed!")
        })

        // go to home
        navigate('/home');
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
                    <InputLabel htmlFor="username">
                        Username
                    </InputLabel>
                    <Input
                        id="username"
                        startAdornment={
                            <InputAdornment position="start">
                                <AccountCircle />
                            </InputAdornment>
                        }
                        onChange={(event) => {
                            setUsername(event.target.value);
                        }}
                    />
                </FormControl>
                <button className="submit" onClick={buttonClickHandler}>Login</button>
            </Stack>
        </div>
    )
}
