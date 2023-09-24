import React from 'react'
import Stack from '@mui/material/Stack';
import IconButton from '@mui/material/IconButton';
import AddIcon from '@mui/icons-material/Add';
import "./Hallway.scss";

export default function Hallway() {
    return (
        <div className='Hallway'>
            <Stack direction="column" spacing={1}>
                <IconButton color="primary">
                    <AddIcon />
                </IconButton>
            </Stack>
        </div>
    )
}
