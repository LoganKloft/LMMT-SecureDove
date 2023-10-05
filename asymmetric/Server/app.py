#!/usr/bin/env python

# standard
import asyncio
import json
import secrets
import uuid
import threading
import time
from datetime import datetime

# installed
import websockets

# to create a profile
# request:
{"type": "profile", "verb": "post", "id": "mid", "content": {"username": "MyName"}}
# response:
{
    "id": "mid",
    "type": "profile",
    "verb": "post",
    "content": {"username": "MyName", "userid": "a valid uuid"},
}

# to create a room
# request:
{"type": "room", "verb": "post", "id": "mid", "content": {"roomname": "MyRoom"}}
# response:
{
    "id": "mid",
    "type": "room",
    "verb": "post",
    "content": {"roomname": "MyRoom", "roomid": "a valid uuid"},
}

# to get a room using uuid
# request:
{"type": "room", "verb": "get", "id": "mid", "content": {"roomid": "a valid uuid"}}
# response: Messages are in order of time sent. The most recent is first.
{
    "type": "room",
    "verb": "get",
    "id": "mid",
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
    "id": "mid",
    "content": {"roomid": "a valid uuid"},
}
# response:
{
    "type": "room",
    "verb": "put",
    "id": "mid",
    "content": {"roomname": "MyRoom", "roomid": "a valid uuid"},
}

# to send a message
# request
{
    "type": "message",
    "verb": "post",
    "id": "mid",
    "content": {"roomid": "a valid uuid", "message": "A message"},
}

# client listen for a new message: - will update message list
{
    "type": "message",
    "verb": "get",
    "id": "mid",
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
    "id": "mid",
    "content": {
        "roomid": "A valid uuid",
        "profiles": ["Logan", "Taylor", "Matthew", "Manjesh"],
    },
}

# client listen for user to join a room - will update user list
{
    "type": "room",
    "verb": "patch",
    "id": "mid",
    "content": {"roomid": "A valid uuid", "username": "New user"},
}

# server sends ACK message for client requests
{"type": "ACK", "verb": "post", "content": {"id": "mid"}}

# server receives ACK message from client
{"type": "ACK", "verb": "post", "content": {"id": "mid"}}

# TODO convert to a class
# uuid -> {"username": "Logan", "socket":socket, "rooms":["uuid1","uuid2"], "userid":"uuid"}
PROFILES = {}

# TODO convert to a class
# uuid -> {"roomname":"room name", "userids"=["uuid1","uuid2"], "messages": [{"header": "Logan @ 9/24/2023 11:25", "message": "A message"}], "roomid":"uuid"}
ROOMS = {}

# when sending a response, we add that to the ACK_QUEUE
# then when the client ACKS it, we remove the response from the 'QUEUE'
# ideally after a TimeToLive (TTL) we resend the response
# message uuid -> message
ACK_QUEUE = {}

connections = 0
max_connections = 10  # not being used right now
requests_received = 0
requests_acked = 0
responses_sent = 0
responses_acked = 0


async def broadcast(sockets, response):
    global responses_sent
    print("===== BROADCAST RESPONSE =====")
    print(response)
    print("")

    for socket in sockets:
        # add response id to each response - creating a new one for each message sent to a profile
        mid = str(uuid.uuid4())
        response["id"] = mid
        ACK_QUEUE[mid] = response
        responses_sent += 1
        await socket.send(json.dumps(response))


async def send(socket, response):
    global responses_sent
    print("===== SINGLE REPONSE =====")
    print(response)
    print("")

    # add response id to response
    mid = str(uuid.uuid4())
    response["id"] = mid
    ACK_QUEUE[mid] = response
    responses_sent += 1
    await socket.send(json.dumps(response))


async def sendAck(socket, request):
    mid = request["id"]
    response = {"type": "ACK", "verb": "post", "content": {"id": mid}}

    print("===== SEND ACK =====")
    print(response)
    print("")

    await socket.send(json.dumps(response))


async def parse(profile):
    """
    Receive, process, and respond to messages from a client.

    """
    global requests_received
    global responses_acked
    global requests_acked

    websocket = profile["socket"]
    async for message in websocket:
        try:
            # Parse a event from the client.
            request = json.loads(message)
            print(request)
            # if type is not ACK we will send a quick ACK
            if request["type"] != "ACK":
                await sendAck(websocket, request)
                requests_acked += 1

            else:
                mid = request["content"]["id"]
                del ACK_QUEUE[mid]
                responses_acked += 1
                continue

            print("===== REQUEST =====")
            print("who: ", profile["username"])
            print(request)
            print("")
            requests_received += 1

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
                    # await websocket.send(json.dumps(response))
                    await send(websocket, response)

                elif request["type"] == "message":
                    # add message to room for new users who join
                    now = datetime.now()
                    now = now.strftime("%d/%m/%Y %H:%M:%S")
                    roomid = request["content"]["roomid"]
                    message = request["content"]["message"]
                    header = f'{profile["username"]} @ {now}'
                    ROOMS[roomid]["messages"].append(
                        {"header": header, "message": message}
                    )

                    # now broadcast single message to everyone in the room (including user sending the message)
                    response = {
                        "type": "message",
                        "verb": "get",
                        "content": {
                            "username": profile["username"],
                            "roomid": roomid,
                            "header": header,
                            "message": message,
                        },
                    }

                    sockets = []
                    for userid in ROOMS[roomid]["userids"]:
                        if PROFILES[userid]["username"] == request["content"]["target"]:
                            sockets.append(PROFILES[userid]["socket"])

                    await broadcast(sockets, response)

                    # for userid in ROOMS[roomid]["userids"]:
                    #     socket = PROFILES[userid]["socket"]
                    #     await socket.send(json.dumps(response))

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

                    # await websocket.send(json.dumps(response))
                    await send(websocket, response)

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

                    # await websocket.send(json.dumps(response))
                    await send(websocket, response)

                    # now broadcast to all users in the room
                    response = {
                        "type": "room",
                        "verb": "patch",
                        "content": {"roomid": roomid, "username": profile["username"]},
                    }

                    sockets = []
                    for userid in ROOMS[roomid]["userids"]:
                        sockets.append(PROFILES[userid]["socket"])

                    await broadcast(sockets, response)
            elif request["verb"] == "dh1":
                roomid = request["content"]["roomid"]

                response = {
                    "type": "room",
                    "verb": "dh1",
                    "content": {
                        "roomid": roomid,
                        "username": profile["username"],
                        "publicKey": request["content"]["publicKey"]
                    },
                }

                sockets = []
                for userid in ROOMS[roomid]["userids"]:
                    sockets.append(PROFILES[userid]["socket"])

                await broadcast(sockets, response)
            elif request["verb"] == "dh2":
                roomid = request["content"]["roomid"]

                response = {
                    "type": "room",
                    "verb": "dh2",
                    "content": {
                        "roomid": roomid,
                        "username": profile["username"],
                        "publicKey": request["content"]["publicKey"]
                    },
                }

                sockets = []
                for userid in ROOMS[roomid]["userids"]:
                    if PROFILES[userid]["username"] == request["content"]["target"]:
                        sockets.append(PROFILES[userid]["socket"])

                await broadcast(sockets, response)

        except Exception as e:
            print("ERROR")
            print(e)


# called when a connection is first established
# we need to create a profile and then respond to future requests
async def handler(websocket):
    """
    Handle a new connection.

    """
    global connections
    connections += 1

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

    await send(websocket, response)

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
                sockets = []
                for userid in ROOMS[roomid]["userids"]:
                    sockets.append(PROFILES[userid]["socket"])

                await broadcast(sockets, response)

        # remove this user's PROFILE entry
        del PROFILES[userid]


def logger():
    global connections
    global requests_acked
    global requests_received
    global responses_acked
    global responses_sent

    while True:
        with open("./audit.txt", "a") as audit:
            now = datetime.now()
            now = now.strftime("%d/%m/%Y %H:%M:%S")
            audit.write(f"time: {now}")
            audit.write(f"connections: {connections}")
            audit.write(f"requests_received: {requests_received}")
            audit.write(f"requests_acked: {requests_acked}")
            audit.write(f"responses_sent: {responses_sent}")
            audit.write(f"responses_acked: {responses_acked}")
        time.sleep(5)


# listen for connections
async def main():
    # for logging every 5 seconds
    thread = threading.Thread(target=logger)
    thread.daemon = True # otherwise will run in background even after ctrl-c on main thread
    thread.start()

    # handle incoming connections
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
