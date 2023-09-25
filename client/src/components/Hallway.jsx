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
import { useNavigate } from 'react-router-dom';
import "./Hallway.scss";

export default function Hallway({ setUsers, setMessages, websocketRef, setCurrentRoomId, currentRoomId }) {
    const [rooms, setRooms] = useState([])
    const [joinValue, setJoinValue] = useState(null);
    const [createValue, setCreateValue] = useState(null);
    const [open, setOpen] = useState(false);

    function handler(websocketRef) {
        websocketRef.current.addEventListener("message", ({ data }) => {
            const response = JSON.parse(data);

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
            else if (response["verb"] === "delete") {
                if (response["type"] === "room") {
                    // re-display users b/c a user left
                    setUsers(response["content"]["profiles"])
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
            let request = {
                "type": "room",
                "verb": "post",
                "content": { "roomname": createValue }
            }

            websocketRef.current.send(JSON.stringify(request));
        }
    }

    const handleClickRoom = (event) => {
        if (websocketRef.current) {
            setCurrentRoomId(event.target.dataset.roomid);

            let request = {
                "type": "room",
                "verb": "get",
                "content": {
                    "roomid": event.target.dataset.roomid
                }
            }

            websocketRef.current.send(JSON.stringify(request));
        }
    }

    const handleJoin = () => {
        handleClose();

        if (websocketRef.current) {
            let request = {
                "type": "room",
                "verb": "put",
                "content": { "roomid": joinValue },
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
                            <IconButton
                                key={room.roomid}
                                onClick={handleClickRoom}>
                                <p className="roomNameLabel" data-roomid={room.roomid}>{room.roomname[0]}</p>
                            </IconButton>
                        )
                    })
                }
                <IconButton onClick={handleClickOpen}>
                    <AddIcon />
                </IconButton>
                <IconButton onClick={handleLogout}>
                    <LogoutIcon />
                </IconButton>
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
                        autoFocus
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
