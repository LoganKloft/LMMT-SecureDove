import React, { useState } from 'react'
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

export default function Hallway({ socket }) {
    const [rooms, setRooms] = useState([{ "roomid": "123456789", "roomname": "test" }])
    const [joinValue, setJoinValue] = useState(null);
    const [createValue, setCreateValue] = useState(null);
    const [open, setOpen] = useState(false);

    const navigate = useNavigate();

    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    const handleCreate = () => {
        handleClose();
    }

    const handleJoin = () => {
        handleClose();
    }

    const handleLogout = () => {
        // close websocket connection

        // navigate to login page
        navigate('/');
    }

    return (
        <div className='Hallway'>
            <Stack direction="column" alignItems={"center"} paddingTop={1} paddingBottom={"10px"} spacing={1}>
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
