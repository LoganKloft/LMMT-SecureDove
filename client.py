#!/usr/bin/env python

import socket
from threading import Thread

s = socket.socket()
port = 8080
s.connect(('x1c9', port))

def connection_handler(s):
    while True:
        print(s.recv(1024).decode())

thread = Thread(target=connection_handler, args=(s,))
thread.start()

while True:
    line = input('')
    s.send(bytes(line, 'utf-8'))

thread.join()

s.close()
