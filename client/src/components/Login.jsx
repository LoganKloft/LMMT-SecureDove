import React, { useState } from 'react'
import Input from '@mui/material/Input';
import InputLabel from '@mui/material/InputLabel';
import InputAdornment from '@mui/material/InputAdornment';
import FormControl from '@mui/material/FormControl';
import AccountCircle from '@mui/icons-material/AccountCircle';
import Stack from '@mui/material/Stack';
import { useNavigate } from 'react-router-dom';
import './Login.scss'

export default function Login() {

    const [username, setUsername] = useState("");

    const navigate = useNavigate();

    function buttonClickHandler() {
        // attempt to create a websocket

        // (later we can enforce unique usernames) if failed:
        // failure due to duplicate username?

        // if successful:
        // go to home page
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
