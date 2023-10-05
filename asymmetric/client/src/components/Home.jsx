import React, { useState, useRef, useEffect } from 'react';
import Hallway from './Hallway';
import Room from './Room';
import "./Home.scss";

export default function Home({ keyObject, publicKey, websocketRef, username }) {
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
	             keyObject={keyObject}
	             publicKey={publicKey}
	             setRoomname={setRoomname} 
		     username={username} />

            {/* room displays messages, users, and sends messages  */}
            <Room sharedSecretKeys={sharedSecretKeys}
	          messages={messages}
	          users={users}
	          currentRoomId={roomIDRef}
	          websocketRef={websocketRef}
		  keyObject={keyObject}
		  publicKey={publicKey}
	          username={username}
	          roomname={roomname} />
        </div>
    )
}
