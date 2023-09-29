import React, { useState, useRef, useEffect } from 'react'
import Hallway from './Hallway';
import Room from './Room';
import "./Home.scss";

export default function Home({ websocketRef }) {

    const [messages, setMessages] = useState([])
    const [users, setUsers] = useState([])
    const [roomname, setRoomname] = useState("");

    const roomIDRef = useRef("");

    return (
        <div className="Home">
            {/* hallway creates and joins rooms */}
            <Hallway setMessages={setMessages} setUsers={setUsers} websocketRef={websocketRef} setCurrentRoomId={(val) => roomIDRef.current = val} currentRoomId={roomIDRef} setRoomname={setRoomname}/>

            {/* room displays messages, users, and sends messages  */}
            <Room messages={messages} users={users} currentRoomId={roomIDRef} websocketRef={websocketRef} roomname={roomname}/>
        </div>
    )
}
