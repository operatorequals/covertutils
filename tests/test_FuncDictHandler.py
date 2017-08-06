import unittest

from covertutils.handlers.impl import SimpleShellHandler
from covertutils.handlers import FunctionDictHandler
from covertutils.orchestration import SimpleOrchestrator
from covertutils.payloads import GenericStages

from os import urandom
from time import sleep
from hashlib import sha512
import re
out_length = 100
in_length = 100


orch1 = SimpleOrchestrator( "passphrase",
	2, out_length, in_length,
	streams = ['main']
	# cycling_algorithm = sha512
	)

orch2 = SimpleOrchestrator( "passphrase",
	2, out_length, in_length,
	# cycling_algorithm = sha512,
	streams = ['main'],
	reverse = True)

chunks = []
def dummy_receive( ) :
	while not chunks :
		sleep(0.1)

	print( "Receiving" )
	return chunks.pop(0)


testable = None

def dummy_send( raw ) :
	global testable
	print( "sending!" )
	stream, message = orch1.depositChunk( raw )
	print( "Sent" )
	if message :
		testable = message


class AgentHandler( FunctionDictHandler ) :


	def onMessage( self, stream, message ) :
		ret = super(AgentHandler, self).onMessage( stream, message )
		print( "Got: " + ret )
		self.preferred_send( ret, 'main' )


class Test_FunctionDictHandler (unittest.TestCase) :

	def setUp( self ) :
		pls = {
			'control' : GenericStages['shellprocess']['marshal'],
			'main' : GenericStages['shellprocess']['marshal'],
		}
		self.p_handler = AgentHandler( dummy_receive, dummy_send, orch2, function_dict = pls )
		print( self.p_handler.getOrchestrator().getStreams() )

	def test_shell_usage( self, ) :
		echoed = '111111111111'
		chunk = orch1.readyMessage( "echo '%s' " % echoed, 'control' )

		chunks.extend( chunk )

		# sleep(0.9)
		# print( '=======================================================' )
		# print( testable )
		while not testable : sleep(0.5)
		# sleep(1)
		print( chunks )
		self.assertTrue( testable.strip() == echoed )
