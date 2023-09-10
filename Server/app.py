#!/usr/bin/env python

# standard
import asyncio
import json
import secrets

# installed
import websockets


JOIN = {}


async def error(websocket, message):
    """
    Send an error message.

    """
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


async def play(websocket, connected):
    """
    Receive and process messages from a client.

    """
    async for message in websocket:
        # Parse a "play" event from the UI.
        event = json.loads(message)
        assert event["type"] == "message"
        message = event["message"]

        try:
            # Print the message.
            print(message)
        except RuntimeError as exc:
            # Send an "error" event if illegal.
            await error(websocket, str(exc))
            continue

        # Send a "message" event to update the UI.
        event = {
            "type": "message",
            "message": message,
        }
        websockets.broadcast(connected, json.dumps(event))


async def start(websocket):
    """
    Handle a connection from the first client: start a new room.

    """
    connected = {websocket}

    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = connected

    try:
        # Send the secret access tokens to the browser of the first player,
        # where they'll be used for building "join" and "watch" links.
        event = {
            "type": "init",
            "join": join_key,
        }
        await websocket.send(json.dumps(event))
        # Receive and process moves from the first player.
        await play(websocket, connected)
    finally:
        del JOIN[join_key]


async def join(websocket, join_key):
    """
    Handle join room requests from clients.

    """
    # Find the room.
    try:
        connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "key not found.")
        return

    # Register to receive messages from this room.
    connected.add(websocket)

    event = {
        "type": "join",
        "message": "new client connected",
    }
    websockets.broadcast(connected, json.dumps(event))

    try:
        # Receive and process messages from this client.
        await play(websocket, connected)
    finally:
        connected.remove(websocket)


async def handler(websocket):
    """
    Handle a connection and dispatch it according to who is connecting.

    """
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "join" in event:
        # Joins an existing room.
        await join(websocket, event["join"])
    else:
        # Starts a new room.
        await start(websocket)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
