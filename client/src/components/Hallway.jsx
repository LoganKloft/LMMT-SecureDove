import React, { useState, useEffect } from 'react'
import Stack from '@mui/material/Stack';
import IconButton from '@mui/material/IconButton';
import AddIcon from '@mui/icons-material/Add';
import LogoutIcon from '@mui/icons-material/Logout';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Tooltip from '@mui/material/Tooltip';
import { GlobalCryptoState } from './CryptoState';
import { v4 as uuidv4 } from 'uuid';
import { useNavigate } from 'react-router-dom';
import fernet from 'fernet';
import "./Hallway.scss";

export default function Hallway({ setUsers, setMessages, websocketRef, setCurrentRoomId, currentRoomId, setRoomname }) {
    const [rooms, setRooms] = useState([])
    const [joinValue, setJoinValue] = useState(null);
    const [createValue, setCreateValue] = useState(null);
    const [open, setOpen] = useState(false);

    function handler(websocketRef) {
        websocketRef.current.addEventListener("message", async ({ data }) => {
            const response = JSON.parse(data);

            if (response["type"] === "profile") {
                if (response["verb"] === "post") {
                    // // server sending us symmetric key
                    // try {
                    //     const textEncoder = new TextEncoder();
                    //     let encoded = textEncoder.encode(response["content"]);
                    //     console.log(encoded);
                    //     console.log(GlobalCryptoState.getKeyPair().privateKey);
                    //     let content = window.crypto.subtle.decrypt(
                    //         {
                    //             name: "RSA-OAEP"
                    //         },
                    //         GlobalCryptoState.getKeyPair().privateKey,
                    //         encoded
                    //     ); // decrypted
                    //     // let dec = new TextDecoder();
                    //     // content = dec.decode(content) // decoded
                    //     // content = JSON.parse(content); // jsonified
                    //     // console.log(content);

                    //     // GlobalCryptoState.setSymmetric(content["symmetric"]);
                    // } catch (e) {
                    //     console.log(e);
                    // }
                    GlobalCryptoState.setSymmetric(response["content"]["symmetric"]);
                    console.log(response);
                    return;
                }
            }

            // messages recieved here have "content" encrypted
            console.log(response["content"]);
            let secret = new fernet.Secret(GlobalCryptoState.getSymmetric());
            let token = new fernet.Token({
                secret: secret,
                token: response["content"],
            });
            let content = token.decode();
            console.log("content", content);
            response["content"] = JSON.parse(content);

            // ACK server responses
            if (response["type"] !== "ACK") {
                let symmetric = GlobalCryptoState.getSymmetric();
                console.log(symmetric.length);
                let secret = new fernet.Secret(symmetric);
                let token = new fernet.Token({
                    secret: secret,
                })

                let content = {
                    "id": response["id"]
                };
                content = JSON.stringify(content);
                content = token.encode(content);

                let request = {
                    "type": "ACK",
                    "verb": "post",
                    "content": content
                }

                websocketRef.current.send(JSON.stringify(request));
            }

            if (response["verb"] === "post") {
                if (response["type"] === "room") {
                    // add to rooms
                    let room = {
                        "roomid": response["content"]["roomid"],
                        "roomname": response["content"]["roomname"]
                    }
                    setRooms(prev => [...prev, room]);
                }
            }
            else if (response["verb"] === "put") {
                if (response["type"] === "room") {
                    // add to rooms
                    let room = {
                        "roomid": response["content"]["roomid"],
                        "roomname": response["content"]["roomname"]
                    }
                    setRooms(prev => [...prev, room])
                }
            }

            // since some of these handlers trigger
            // ui changes, we only want them to occur when it
            // makes sense. this depends on whether the 
            // current room we're displaying matches the
            // one a response refers to. The exceptions are
            // responses that create a new room (which is above this statement)
            if (currentRoomId.current !== response["content"]["roomid"]) {
                return;
            }

            if (response["verb"] === "get") {
                if (response["type"] === "room") {
                    // update messages
                    setMessages(response["content"]["messages"])

                    // update users
                    setUsers(response["content"]["profiles"])

                    // update roomname
                    setRoomname(response["content"]["roomname"])
                }
                else if (response["type"] === "message") {
                    // add a new message
                    let message = {
                        "header": response["content"]["header"],
                        "message": response["content"]["message"]
                    }
                    setMessages(prev => [...prev, message])
                }
            }
            else if (response["verb"] === "delete") {
                if (response["type"] === "room") {
                    // re-display users b/c a user left
                    setUsers(response["content"]["profiles"])
                }
            }
            else if (response["verb"] === "patch") {
                if (response["type"] === "room") {
                    // we see this message when a new user has joined the room
                    let username = response["content"]["username"]
                    setUsers(prev => [...prev, username])
                }
            }
        })
    }

    useEffect(() => {
        handler(websocketRef)
    }, [websocketRef])

    const navigate = useNavigate();

    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    const handleCreate = () => {
        handleClose();

        if (websocketRef.current) {
            let symmetric = GlobalCryptoState.getSymmetric();
            console.log(symmetric.length);
            let secret = new fernet.Secret(symmetric);
            let token = new fernet.Token({
                secret: secret,
            })

            let content = { "roomname": createValue };
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
        }
    }

    const handleClickRoom = (event) => {
        if (websocketRef.current) {
            setCurrentRoomId(event.target.dataset.roomid);

            let symmetric = GlobalCryptoState.getSymmetric();
            console.log(symmetric.length);
            let secret = new fernet.Secret(symmetric);
            let token = new fernet.Token({
                secret: secret,
            })

            let content = {
                "roomid": event.target.dataset.roomid
            };
            content = JSON.stringify(content);
            content = token.encode(content);

            let request = {
                "type": "room",
                "verb": "get",
                "id": uuidv4(),
                "content": content
            }

            websocketRef.current.send(JSON.stringify(request));
        }
    }

    const handleJoin = () => {
        handleClose();

        let symmetric = GlobalCryptoState.getSymmetric();
        console.log(symmetric.length);
        let secret = new fernet.Secret(symmetric);
        let token = new fernet.Token({
            secret: secret,
        })

        let content = { "roomid": joinValue };
        content = JSON.stringify(content);
        content = token.encode(content);

        if (websocketRef.current) {
            let request = {
                "type": "room",
                "verb": "put",
                "id": uuidv4(),
                "content": content,
            }

            websocketRef.current.send(JSON.stringify(request));
        }
    }

    const handleLogout = () => {
        // close websocket connection
        if (websocketRef.current) {
            websocketRef.current.close()
        }

        // navigate to login page
        navigate('/');
    }

    return (
        <div className='Hallway'>
            <Stack direction="column" alignItems={"center"} paddingTop={1} paddingBottom={"10px"} spacing={1}>
                {
                    rooms &&
                    rooms.map(room => {
                        return (
                            <Tooltip key={room.roomid} title={room.roomname}>
                                <IconButton
                                    onClick={handleClickRoom}>
                                    <p className="roomNameLabel" data-roomid={room.roomid}>{room.roomname[0]}</p>
                                </IconButton>
                            </Tooltip>
                        )
                    })
                }
                <Tooltip title="Create or join a room">
                    <IconButton onClick={handleClickOpen}>
                        <AddIcon />
                    </IconButton>
                </Tooltip>
                <Tooltip title="Exit">
                    <IconButton onClick={handleLogout}>
                        <LogoutIcon />
                    </IconButton>
                </Tooltip>
            </Stack>

            <Dialog open={open} onClose={handleClose}>
                <DialogTitle>Room Manager</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Enter a name to create a room or join an existing room using its id.
                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        id="create"
                        label="New room name"
                        fullWidth
                        variant="standard"
                        onChange={(event) => {
                            setCreateValue(event.target.value);
                        }}
                    />
                    <Button onClick={handleCreate}>Create</Button>
                    <TextField
                        margin="dense"
                        id="join"
                        label="Existing room id"
                        fullWidth
                        variant="standard"
                        onChange={(event) => {
                            setJoinValue(event.target.value);
                        }}
                    />
                    <Button onClick={handleJoin}>Join</Button>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Cancel</Button>
                </DialogActions>
            </Dialog>
        </div>
    )
}
