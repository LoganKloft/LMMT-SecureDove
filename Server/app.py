#!/usr/bin/env python

# standard
import asyncio
import json
import secrets
import uuid
import threading
import time
import base64
from datetime import datetime

# installed
import websockets

# import rsa
from cryptography.fernet import Fernet  # symmetric encryption
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

# when a client wants to create a profile, it will establish a symmetric key with the server
# communication between client and server will use this symmetric key for all messages

# when a client wants to create a room, a symmetric key will be created for that room
# the client will be sent the symmetric key

# when future clients join the room they will receieve the symmetric key from the server

# this means that the server stores all symmetric keys!

# How to accomplish the above?
# each client will generate a public / private key pair before the create profile request is sent
# when a profile request is sent, the client will include its public key
# then the server will generate a symmetric key and use the profile's public key to encrypt it
# the profile will then decrypt the symmetric key and store it
# now all messages will be encrypted and decrypted using this symmetric key

# when a client creates a room, the server will generate a new symmetric key for that room
# when a client joins a chat room, the server will use the client's public key to send the symmetric key for the room
# all room messages will use this symmetric key in addition to the overall request being encypted using the first symmetric key

# symmetric encryption: Fernet - guarantees confidentiality AND integrity (throw error if message tampering detected)
# asymmetric encryption:

# to create a profile
# request:
{
    "type": "profile",
    "verb": "post",
    "id": "mid",
    "content": {"username": "MyName", "public": "client's public key"},
}
# response:
{
    "id": "mid",
    "type": "profile",
    "verb": "post",
    "content": {
        "username": "MyName",
        "userid": "a valid uuid",
        "symmetric": "shared symmetric key",
    },
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
# response: update hallway, but won't actually put user in the room until they click the hallway icon!!
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


async def broadcast(profiles, response):
    global responses_sent
    print("===== BROADCAST RESPONSE =====")
    print(response)
    print("")

    for profile in profiles:
        # add response id to each response - creating a new one for each message sent to a profile
        socket = profile["socket"]
        mid = str(uuid.uuid4())
        response["id"] = mid
        response["userid"] = profile[
            "userid"
        ]  # so we know who to resend the message to
        response[
            "ack_timestamp"
        ] = time.time()  # so we can track when to resend - every five seconds
        response["useEncryptedSend"] = False
        ACK_QUEUE[mid] = response
        responses_sent += 1
        await socket.send(json.dumps(response))


async def broadcastEncrypted(profiles, response):
    global responses_sent
    print("===== BROADCAST ENCRYPTED RESPONSE =====")
    print(response)
    print("")
    print(profiles)

    saved_content = response["content"]

    for profile in profiles:
        # add response id to each response - creating a new one for each message sent to a profile
        socket = profile["socket"]
        mid = str(uuid.uuid4())
        response["id"] = mid  # unique id for ACK
        response["userid"] = profile[
            "userid"
        ]  # so we know who to resend the message to
        response[
            "ack_timestamp"
        ] = time.time()  # so we can track when to resend - every five seconds
        response["useEncryptedSend"] = True
        ACK_QUEUE[mid] = response
        responses_sent += 1

        # encrypt content
        fernet = Fernet(profile["symmetric"])
        content = json.dumps(saved_content)
        content = fernet.encrypt(content.encode()).decode()
        response["content"] = content

        await socket.send(json.dumps(response))


async def send(profile, response):
    global responses_sent
    print("===== SINGLE REPONSE =====")
    print(response)
    print("")

    # add response id to response
    socket = profile["socket"]
    mid = str(uuid.uuid4())
    response["id"] = mid
    response["userid"] = profile["userid"]  # so we know who to resend the message to
    response[
        "ack_timestamp"
    ] = time.time()  # so we can track when to resend - every five seconds
    response["useEncryptedSend"] = False
    ACK_QUEUE[mid] = response
    responses_sent += 1
    await socket.send(json.dumps(response))


async def sendEncrypted(profile, response):
    global responses_sent
    print("===== SINGLE REPONSE =====")
    print(response)
    print("")

    # add response id to response
    socket = profile["socket"]
    mid = str(uuid.uuid4())
    response["id"] = mid
    response["userid"] = profile["userid"]  # so we know who to resend the message to
    response[
        "ack_timestamp"
    ] = time.time()  # so we can track when to resend - every five seconds
    response["useEncryptedSend"] = True
    ACK_QUEUE[mid] = response
    responses_sent += 1

    # encrypt content
    fernet = Fernet(profile["symmetric"])
    content = json.dumps(response["content"])
    content = fernet.encrypt(content.encode()).decode()
    response["content"] = content

    await socket.send(json.dumps(response))


async def sendAck(profile, request):
    socket = profile["socket"]
    mid = request["id"]
    response = {"type": "ACK", "verb": "post", "content": {"id": mid}}

    print("===== SEND ACK =====")
    print(response)
    print("")

    await socket.send(json.dumps(response))


async def sendAckEncrypted(profile, request):
    socket = profile["socket"]
    mid = request["id"]
    response = {"type": "ACK", "verb": "post", "content": {"id": mid}}

    print("===== SEND ACK ENCRYPTED =====")
    print(response)
    print("")

    # encrypt content
    fernet = Fernet(profile["symmetric"])
    content = json.dumps(response["content"])
    content = fernet.encrypt(content.encode()).decode()
    response["content"] = content
    await socket.send(json.dumps(response))


async def parse(profile):
    """
    Receive, process, and respond to messages from a client.
    All received messsages are encrypted.

    """
    global requests_received
    global responses_acked
    global requests_acked

    async for message in profile["socket"]:
        try:
            # Parse a event from the client.
            request = json.loads(message)

            # decrypt content
            fernet = Fernet(profile["symmetric"])
            content = request["content"]  # an encrypted string
            print("IN PARSER")
            print(content)
            content = fernet.decrypt(content)  # a decrypted byte string
            content = content.decode()  # a string of json
            content = json.loads(content)  # json
            request["content"] = content
            print("FINISH DECODE")
            print(request)
            # if type is not ACK we will send a quick ACK
            if request["type"] != "ACK":
                await sendAckEncrypted(profile, request)
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
                    await sendEncrypted(profile, response)

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
                            "roomid": roomid,
                            "header": header,
                            "message": message,
                        },
                    }

                    profiles = []
                    for userid in ROOMS[roomid]["userids"]:
                        profiles.append(PROFILES[userid])

                    await broadcastEncrypted(profiles, response)

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
                    await sendEncrypted(profile, response)

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
                    await sendEncrypted(profile, response)

                    # now broadcast to all users in the room
                    response = {
                        "type": "room",
                        "verb": "patch",
                        "content": {"roomid": roomid, "username": profile["username"]},
                    }

                    profiles = []
                    for userid in ROOMS[roomid]["userids"]:
                        profiles.append(PROFILES[userid])

                    await broadcastEncrypted(profiles, response)

        except Exception as e:
            print("ERROR")
            print(e)


async def isValidUsername(username):
    # username must be a string
    if not isinstance(username, str):
        return False

    # usernmae must be at least one character and no more than 32
    if len(username) < 1 or len(username) > 32:
        return False

    # username may only contain characters and numbers
    if not username.isalnum():
        return False

    # username must be unique
    for key, value in PROFILES.items():
        if value["username"] == username:
            return False

    return True


# called when a connection is first established
# we need to create a profile and then respond to future requests
async def handler(websocket):
    """
    Handle a new connection.

    """
    global connections
    connections += 1

    # wait for the first request
    request = None
    while True:
        event = await websocket.recv()
        request = json.loads(event)
        print("========= Login Request =========")
        print(request)
        print("========= End Login Request =========\n")

        valid = await isValidUsername(request["content"]["username"])
        if valid:
            break

        response = {"type": "profile", "verb": "post", "content": {"status": False}}
        await websocket.send(json.dumps(response))

    # We are assuming first event is the create profile event
    userid = str(uuid.uuid4())
    username = request["content"]["username"]
    # public = RSA.import_key(request["content"]["public"])

    # generate symmetric key for the profile
    key = Fernet.generate_key()
    symmetric = key.decode()
    pub_key = RSA.importKey(request["content"]["public"])
    # cipher = PKCS1_OAEP.new(pub_key)
    cipher = PKCS1_v1_5.new(pub_key)
    ciphertext = cipher.encrypt(bytes(symmetric, "utf-8"))
    print(base64.b64encode(ciphertext))

    pri_key = RSA.importKey(request["content"]["private"])
    # pri_cipher = PKCS1_OAEP.new(pri_key)
    pri_cipher = PKCS1_v1_5.new(pri_key)
    sentinel = get_random_bytes(16)
    plaintext = pri_cipher.decrypt(ciphertext, sentinel)
    print(plaintext)

    encrypted_symmetric = base64.b64encode(ciphertext).decode("ascii")
    print(pri_cipher.decrypt(base64.b64decode(encrypted_symmetric), sentinel))

    # create content value
    # content = json.dumps(
    #     {"username": username, "userid": userid, "symmetric": key.decode()}
    # )
    content = {
        "username": username,
        "userid": userid,
        "symmetric": symmetric,
        "encrypted_symmetric": base64.b64encode(ciphertext).decode("ascii"),
        "status": True,
    }

    # encrypt content using client's public key
    # print("FIRST")
    # print(public)
    # print("END FIRST")
    # encryptor = PKCS1_OAEP.new(public)
    # encrypted_msg = encryptor.encrypt(content.encode())
    # content = base64.b64encode(encrypted_msg)
    # content = content.decode("utf-8")
    # private = RSA.import_key(request["content"]["private"])
    # decryptor = PKCS1_OAEP.new(private)
    # msg = decryptor.decrypt(encrypted_msg)
    # print("SECOND")
    # print(msg)
    # print("END SECOND")

    # create profile
    PROFILES[userid] = {
        "username": username,
        "socket": websocket,
        "rooms": [],
        "userid": userid,
        "symmetric": key,
    }
    profile = PROFILES[userid]

    # send to client
    response = {
        "type": "profile",
        "verb": "post",
        "content": content,
    }
    await send(profile, response)

    try:
        # listen for all incoming messages (which are encrypted using symmetric)
        await parse(profile)

    finally:
        # socket disconnect
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
                profiles = []
                for userid in ROOMS[roomid]["userids"]:
                    profiles.append(PROFILES[userid])

                await broadcastEncrypted(profiles, response)

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


# every 5 seconds will iterate through all items in the ACK queue
# if that item is is type="message" and it's been 5 seconds since sending,
# we will rebroadcast it
def rebroadcaster():
    # for all entries with type="message"
    # check that user still exists
    # if not delete entry
    # check that current timestamp and saved timestamp differ by 5 or more seconds
    # then delete the entry
    # then send the message again using send or sendEncrypted
    for mid, response in ACK_QUEUE.items():
        if response["type"] == "message" and response["verb"] == "post":
            userid = response["userid"]
            if userid in PROFILES:
                cur_timestamp = time.time()
                ack_timestamp = response["ack_timestamp"]

                if cur_timestamp - ack_timestamp >= 5:
                    del ACK_QUEUE[mid]

                    if response["useEncryptedSend"] == True:
                        sendEncrypted(PROFILES[userid], response)
                    else:
                        send(PROFILES[userid], response)
            else:
                del ACK_QUEUE[mid]
    time.sleep(5)


# listen for connections
async def main():
    # for logging every 5 seconds
    logger_thread = threading.Thread(target=logger)
    logger_thread.daemon = (
        True  # otherwise will run in background even after ctrl-c on main thread
    )
    logger_thread.start()

    # for rebroadcasting messages that heven't been ACKed
    rebroadcaster_thread = threading.Thread(target=rebroadcaster)
    rebroadcaster_thread.daemon = True
    rebroadcaster_thread.start()

    # handle incoming connections
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
