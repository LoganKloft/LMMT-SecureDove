import React, { useState, useRef, useEffect } from 'react';
import Hallway from './Hallway';
import Room from './Room';
import "./Home.scss";

export default function Home({ websocketRef, username }) {
    const [messages, setMessages] = useState([]);
    const [users, setUsers] = useState([]);
    const [roomname, setRoomname] = useState("");
    const [sharedSecretKeys, setSharedSecretKeys] = useState({});

    const roomIDRef = useRef("");

    return (
        <div className="Home">
            {/* hallway creates and joins rooms */}
            <Hallway setSharedSecretKeys={setSharedSecretKeys}
		     sharedSecretKeys={sharedSecretKeys}
	             setMessages={setMessages}
	             setUsers={setUsers}
	             websocketRef={websocketRef}
	             setCurrentRoomId={(val) => roomIDRef.current = val}
	             currentRoomId={roomIDRef}
	             setRoomname={setRoomname} 
		     username={username} />

            {/* room displays messages, users, and sends messages  */}
            <Room sharedSecretKeys={sharedSecretKeys}
	          messages={messages}
	          users={users}
	          currentRoomId={roomIDRef}
	          websocketRef={websocketRef}
	          username={username}
	          roomname={roomname} />
        </div>
    )
}
