from covertutils.shells.subshells import SimpleSubShell

import socket
import threading
from time import sleep


def meterpreter_proxy( proxy_socket, instance ) :
	print ("Started Meterpreter Proxy thread")
	# b = 42245
	b = 1024
	while True :
		# print "recv'ing",
		resp = proxy_socket.recv(b)
		# print "recv()'d %d bytes of data'" % b
		print resp.encode('hex')
		instance.handler.preferred_send( resp, instance.stream )
		sleep(0.1)
		# b = 8

class MeterpreterShell ( SimpleSubShell ) :

# 	intro = """
# This is an Example Shell. It has a custom prompt, and reverses all input before sending to the stage.
# 	"""

	def __init__( self, stream, handler, queue_dict, base_shell, ignore_messages = set(), prompt_templ = "{stream}> ") :
		SimpleSubShell.__init__( self, stream, handler, queue_dict, base_shell, ignore_messages, prompt_templ )
		"""A method that uses the `prompt_templ` argument
		to reformat the prompt
		(in case the `format()` {tags} have changed)"""
		self.updatePrompt()

		def meterpreter_send(message, instance) :
			print ("Forwarding meterpreter message")
			print "[!] '%s'" % message
			instance.proxy.send(message)

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
