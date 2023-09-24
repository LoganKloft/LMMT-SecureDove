#!/usr/bin/env python

# standard
import asyncio
import json
import secrets
import uuid
from datetime import datetime

# installed
import websockets

# to create a profile
# request:
{"type": "profile", "verb": "post", "content": {"username": "MyName"}}
# response:
{
    "type": "profile",
    "verb": "post",
    "content": {"username": "MyName", "userid": "a valid uuid"},
}

# to create a room
# request:
{"type": "room", "verb": "post", "content": {"roomname": "MyRoom"}}
# response:
{
    "type": "room",
    "verb": "post",
    "content": {"roomname": "MyRoom", "roomid": "a valid uuid"},
}

# to get a room using uuid
# request:
{"type": "room", "verb": "get", "content": {"roomid": "a valid uuid"}}
# response: Messages are in order of time sent. The most recent is first.
{
    "type": "room",
    "verb": "get",
    "content": {
        "roomid": "a valid uuid",
        "roomname": "RoomName",
        "profiles": ["Logan", "Taylor", "Matthew", "Manjesh"],
        "messages": [{"header": "Logan @ 9/24/2023 11:25", "message": "A message"}],
    },
}

# to join a room
# request:
{
    "type": "room",
    "verb": "put",
    "content": {"roomid": "a valid uuid"},
}
# response:
{
    "type": "room",
    "verb": "put",
    "content": {"roomname": "MyRoom", "roomid": "a valid uuid"},
}

# to send a message
# request
{
    "type": "message",
    "verb": "post",
    "content": {"roomid": "a valid uuid", "message": "A message"},
}

# client listen for a new message:
{
    "type": "message",
    "verb": "get",
    "content": {
        "roomid": "A valid uuid",
        "header": "Logan @ 9/24/2023 11:25",
        "message": "A message",
    },
}

# client listen for user to leave a room
{
    "type": "room",
    "verb": "delete",
    "content": {
        "roomid": "A valid uuid",
        "profiles": ["Logan", "Taylor", "Matthew", "Manjesh"],
    },
}

# TODO convert to a class
# uuid -> {"username": "Logan", "socket":socket, "rooms":["uuid1","uuid2"], "userid":"uuid"}
PROFILES = {}

# TODO convert to a class
# uuid -> {"roomname":"room name", "userids"=["uuid1","uuid2"], "messages": [{"header": "Logan @ 9/24/2023 11:25", "message": "A message"}], "roomid":"uuid"}
ROOMS = {}


async def parse(profile):
    """
    Receive, process, and respond to messages from a client.

    """
    websocket = profile["socket"]
    async for message in websocket:
        # Parse a event from the client.
        request = json.loads(message)

        if request["verb"] == "post":
            if request["type"] == "room":
                # create a room
                roomid = str(uuid.uuid4())
                roomname = request["content"]["roomname"]

                ROOMS[roomid] = {
                    "roomname": roomname,
                    "userids": [profile["userid"]],
                    "messages": [],
                    "roomid": roomid,
                }

                # emit event to user so they can update ui
                response = {
                    "type": "room",
                    "verb": "post",
                    "content": {"roomname": roomname, "roomid": roomid},
                }
                await websocket.send(json.dumps(response))

            elif request["type"] == "message":
                # add message to room for new users who join
                now = datetime.now()
                now = now.strftime("%d/%m/%Y %H:%M:%S")
                roomid = request["content"]["roomid"]
                message = request["content"]["message"]
                header = f'{profile["username"]} @ {now}'
                ROOMS[roomid]["messages"].append({"header": header, "message": message})

                # now broadcast single message to everyone in the room (including user sending the message)
                response = {
                    "type": "message",
                    "verb": "get",
                    "content": {
                        "roomid": roomid,
                        "header": header,
                        "message": message,
                    },
                }

                for userid in ROOMS[roomid]["userids"]:
                    socket = PROFILES[userid]["socket"]
                    await socket.send(json.dumps(response))

        elif request["verb"] == "get":
            if request["type"] == "room":
                roomid = request["content"]["roomid"]
                roomname = ROOMS[roomid]["roomname"]
                profiles = list(
                    map(
                        lambda userid: PROFILES[userid]["username"],
                        ROOMS[roomid]["userids"],
                    )
                )
                response = {
                    "type": "room",
                    "verb": "get",
                    "content": {
                        "roomid": roomid,
                        "roomname": roomname,
                        "profiles": profiles,
                        "messages": ROOMS[roomid]["messages"],
                    },
                }

                await websocket.send(json.dumps(response))

        elif request["verb"] == "put":
            if request["type"] == "room":
                roomid = request["content"]["roomid"]

                # add user to room
                ROOMS[roomid]["userids"].append(profile["userid"])

                response = {
                    "type": "room",
                    "verb": "put",
                    "content": {
                        "roomname": ROOMS[roomid]["roomname"],
                        "roomid": roomid,
                    },
                }

                await websocket.send(json.dumps(response))


# called when a connection is first established
# we need to create a profile and then respond to future requests
async def handler(websocket):
    """
    Handle a new connection.

    """
    # wait for the first request
    event = await websocket.recv()
    request = json.loads(event)

    # We are assuming first event is the create profile event
    userid = str(uuid.uuid4())
    username = request["content"]["username"]

    PROFILES[userid] = {
        "username": username,
        "socket": websocket,
        "rooms": [],
        "userid": userid,
    }
    profile = PROFILES[userid]

    response = {
        "type": "profile",
        "verb": "post",
        "content": {"username": username, "userid": userid},
    }

    await websocket.send(json.dumps(response))

    try:
        await parse(profile)

    finally:
        # for each room this user is a part of:
        for roomid in profile["rooms"]:
            # remove the user from that room
            ROOMS[roomid]["userids"].remove(userid)

            # if no more users left in the room:
            if not ROOMS[roomid]["userids"]:
                # delete the ROOM entry
                del ROOMS[roomid]

            # if users left in the room broadcast update
            else:
                profiles = list(
                    map(
                        lambda userid: PROFILES[userid]["name"],
                        ROOMS[roomid]["userids"],
                    )
                )

                response = {
                    "type": "room",
                    "verb": "delete",
                    "content": {
                        "roomid": roomid,
                        "profiles": profiles,
                    },
                }

                # broadcast the updated list of room profiles
                for userid in ROOMS[roomid]["userids"]:
                    socket = PROFILES[userid]["socket"]
                    await socket.send(json.dumps(response))

        # remove this user's PROFILE entry
        del PROFILES[userid]


# listen for connections
async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
