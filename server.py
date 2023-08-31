#!/usr/bin/env python

import os
import socket
from threading import Thread

# TODO: Add a lock to make sure there are no conflicts.
threads = []
sockets = []

def connection_handler(conn, addr):
    print(f'Handling connection from {addr}')

    while True:
        line = conn.recv(1024)
        if len(line) <= 0: break
        print(f'<{addr[1]}> {line.decode()}')

        for s in sockets:
            if s == conn: continue
            s.send(f'<{addr[1]}> {line.decode()}'.encode())

    conn.close()

s = socket.socket()
host = 'localhost'
port = 8080
print(f'Listening at {host}:{port}')
s.bind((host, port))
s.listen(1)

while True:
    conn, addr = s.accept()
    thread = Thread(target=connection_handler, args=(conn, addr))
    thread.start()
    threads.append(thread)
    sockets.append(conn)

for thread in threads:
    thread.join()
