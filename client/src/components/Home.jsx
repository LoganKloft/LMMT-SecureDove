import React from 'react'
import Hallway from './Hallway';
import Room from './Room';
import "./Home.scss";

export default function Home() {
    return (
        <div className="Home">
            {/* hallway sends back which room to join as a uuid */}
            <Hallway />

            {/* pass in  */}
            <Room />
        </div>
    )
}
