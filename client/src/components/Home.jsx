import React, { useState, useRef } from 'react'
import Hallway from './Hallway';
import Room from './Room';
import "./Home.scss";

export default function Home({ websocketRef }) {

    const [messages, setMessages] = useState([])
    const [users, setUsers] = useState([])
    const [currentRoomId, setCurrentRoomId] = useState("")

    return (
        <div className="Home">
            {/* hallway creates and joins rooms */}
            <Hallway setMessages={setMessages} setUsers={setUsers} websocketRef={websocketRef} setCurrentRoomId={setCurrentRoomId} currentRoomId={currentRoomId} />

            {/* room displays messages, users, and sends messages  */}
            <Room messages={messages} users={users} currentRoomId={currentRoomId} websocketRef={websocketRef} />
        </div>
    )
}
