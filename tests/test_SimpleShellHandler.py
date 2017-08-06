import unittest

from covertutils.handlers.impl import SimpleShellHandler
from covertutils.orchestration import SimpleOrchestrator

from os import urandom
from time import sleep
from hashlib import sha512
import re
out_length = 4
in_length = 4


orch1 = SimpleOrchestrator( "passphrase",
	2, out_length, in_length,
	# cycling_algorithm = sha512
	)

orch2 = SimpleOrchestrator( "passphrase",
	2, out_length, in_length,
	# cycling_algorithm = sha512,
	reverse = True)

chunks = []
def dummy_receive( ) :
	while not chunks :
		sleep(0.1)
	# print "Receiving"
	return chunks.pop(0)


testable = None

def dummy_send( raw ) :
	global testable
	# print "sending!"
	stream, message = orch1.depositChunk( raw )
	if message :
		testable = message



class Test_ShellHandler (unittest.TestCase) :

	def setUp( self ) :
		self.p_handler = SimpleShellHandler( dummy_receive, dummy_send, orch2 )

	def test_shell_usage( self, ) :
		echoed = '111111111111'
		chunk = orch1.readyMessage( "echo '%s' " % echoed )	# In SimpleShellHandler all communication goes through the 'control' stream

		chunks.extend( chunk )
		# sleep(0.9)
		# print '======================================================='
		# print testable
		while not testable : sleep(0.5)
		self.assertTrue( testable.strip() == echoed )
