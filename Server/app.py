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

# client listen for a new message: - will update message list
{
    "type": "message",
    "verb": "get",
    "content": {
        "roomid": "A valid uuid",
        "header": "Logan @ 9/24/2023 11:25",
        "message": "A message",
    },
}

# client listen for user to leave a room - will update user list
{
    "type": "room",
    "verb": "delete",
    "content": {
        "roomid": "A valid uuid",
        "profiles": ["Logan", "Taylor", "Matthew", "Manjesh"],
    },
}

# client listen for user to join a room - will update user list
{
    "type": "room",
    "verb": "patch",
    "content": {"roomid": "A valid uuid", "username": "New user"},
}


#   The variables are now combined into one class that being the Information class which handles the parsing
#   of the profile

class INFORMATION:
    def __init__(self):
        self.PROFILES = {}
        self.ROOMS = {}

    async def parse(self):
        """
        Receive, process, and respond to messages from a client.
        """
        profile = self.PROFILES[list(self.PROFILES.keys())[0]]
        # print(profile,type(profile))

        websocket = profile["socket"]
        async for message in websocket:
            # Parse a event from the client.
            request = json.loads(message)

            print("===== REQUEST =====")
            print("who: ", profile["username"])
            print(request)
            print("")

            if request["verb"] == "post":
                if request["type"] == "room":
                    # create a room
                    roomid = str(uuid.uuid4())
                    roomname = request["content"]["roomname"]

                    self.ROOMS[roomid] = {
                        "roomname": roomname,
                        "userids": [profile["userid"]],
                        "messages": [],
                        "roomid": roomid,
                    }
                    # print(ROOMS.values)
                    # emit event to user so they can update ui
                    response = {
                        "type": "room",
                        "verb": "post",
                        "content": {"roomname": roomname, "roomid": roomid},
                    }
                    # await websocket.send(json.dumps(response))
                    await send(websocket, response)

                elif request["type"] == "message":
                    # add message to room for new users who join
                    now = datetime.now()
                    now = now.strftime("%d/%m/%Y %H:%M:%S")
                    roomid = request["content"]["roomid"]
                    message = request["content"]["message"]
                    header = f'{profile["username"]} @ {now}'
                    self.ROOMS[roomid]["messages"].append({"header": header, "message": message})

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

                    sockets = []
                    for userid in self.ROOMS[roomid]["userids"]:
                        sockets.append(self.PROFILES[userid]["socket"])

                    await broadcast(sockets, response)

                    # for userid in ROOMS[roomid]["userids"]:
                    #     socket = PROFILES[userid]["socket"]
                    #     await socket.send(json.dumps(response))

            elif request["verb"] == "get":
                if request["type"] == "room":
                    roomid = request["content"]["roomid"]
                    roomname = self.ROOMS[roomid]["roomname"]
                    profiles = list(
                        map(
                            lambda userid: self.PROFILES[userid]["username"],
                            self.ROOMS[roomid]["userids"],
                        )
                    )
                    response = {
                        "type": "room",
                        "verb": "get",
                        "content": {
                            "roomid": roomid,
                            "roomname": roomname,
                            "profiles": profiles,
                            "messages": self.ROOMS[roomid]["messages"],
                        },
                    }

                    # await websocket.send(json.dumps(response))
                    await send(websocket, response)

            elif request["verb"] == "put":
                if request["type"] == "room":
                    roomid = request["content"]["roomid"]
                    # print(roomid)

                    # # add user to room
                    # print(ROOMS.values)
                    # print(roomid)
                    self.ROOMS[roomid]["userids"].append(profile["userid"])

                    response = {
                        "type": "room",
                        "verb": "put",
                        "content": {
                            "roomname": self.ROOMS[roomid]["roomname"],
                            "roomid": roomid,
                        },
                    }

                    # await websocket.send(json.dumps(response))
                    await send(websocket, response)

                    # now broadcast to all users in the room
                    response = {
                        "type": "room",
                        "verb": "patch",
                        "content": {"roomid": roomid, "username": profile["username"]},
                    }

                    sockets = []
                    for userid in self.ROOMS[roomid]["userids"]:
                        sockets.append(self.values[userid]["socket"])

                    await broadcast(sockets, response)


async def broadcast(sockets, response):
    print("===== BROADCAST RESPONSE =====")
    print(response)
    print("")

    for socket in sockets:
        await socket.send(json.dumps(response))


async def send(socket, response):
    print("===== SINGLE REPONSE =====")
    print(response)
    print("")

    await socket.send(json.dumps(response))

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

    INFO.PROFILES[userid] = {
        "username": username,
        "socket": websocket,
        "rooms": [],
        "userid": userid,
    }
    profile = INFO.PROFILES[userid]
    # print(list(PROFILES.values.keys())[0])
    response = {
        "type": "profile",
        "verb": "post",
        "content": {"username": username, "userid": userid},
    }

    await websocket.send(json.dumps(response))

    try:
        await INFO.parse()

    finally:
        # for each room this user is a part of:
        for roomid in profile["rooms"]:
            # remove the user from that room
            INFO.ROOMS[roomid]["userids"].remove(userid)

            # if no more users left in the room:
            if not INFO.ROOMS[roomid]["userids"]:
                # delete the ROOM entry
                del INFO.ROOMS[roomid]

            # if users left in the room broadcast update
            else:
                profiles = list(
                    map(
                        lambda userid: INFO.PROFILES[userid]["name"],
                        INFO.ROOMS[roomid]["userids"],
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
                for userid in INFO.ROOMS[roomid]["userids"]:
                    socket = INFO.PROFILES[userid]["socket"]
                    await socket.send(json.dumps(response))

        # remove this user's PROFILE entry
        del INFO.PROFILES[userid]




# This variable stores all the information needed to run the program in the backend.
INFO = INFORMATION()

# listen for connections
async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
