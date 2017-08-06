import unittest

from covertutils.handlers.impl import SimpleShellHandler
from covertutils.handlers import StageableHandler
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
	streams = ['main', 'control', 'stage'],
	# streams = ['main']
	# cycling_algorithm = sha512
	)

orch2 = SimpleOrchestrator( "passphrase",
	2, out_length, in_length,
	# cycling_algorithm = sha512,
	streams = ['main', 'control', 'stage'],
	# streams = ['main'],
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
	print( "Sent '%s' in %s" % ( message, stream ) )
	if message :
		testable = message


class AgentHandler( StageableHandler ) :

	def onMessage( self, stream, message ) :
		ret = super(AgentHandler, self).onMessage( stream, message )
		print( message )
		print( "Got: "+ret )
		if ret not in self.orchestrator.getStreams() :
			self.preferred_send( ret, 'main' )


class Test_StageableHandler (unittest.TestCase) :

	def setUp( self ) :
		pls = {
			'control' : GenericStages['shellprocess']['marshal'],
			'main' : GenericStages['shellprocess']['marshal'],
		}
		self.p_handler = AgentHandler( dummy_receive, dummy_send, orch2, function_dict = pls )
		print( self.p_handler.getOrchestrator().getStreams() )

	def test_stage_addition( self, ) :

		r_stream = urandom(4).encode('hex')
		stage_obj = StageableHandler.createStageMessage(r_stream, GenericStages['echo']['marshal'])
		# print( self.p_handler.orchestrator.streams_buckets[self.p_handler.stage_stream] )

		chunk = orch1.readyMessage( stage_obj, 'stage' )
		# chunk = orch1.readyMessage( stage_obj, self.p_handler.stage_stream )
		# chunk = orch1.readyMessage( stage_obj, 'stage')
		chunks.extend( chunk )



		sleep(1)
		# while not
		echoed = '111111111111'
		orch1.addStream( r_stream )
		chunk = orch1.readyMessage( echoed, r_stream )

		chunks.extend( chunk )

		# sleep(0.9)
		# print( '=======================================================' )
		# print( testable )
		while not testable : sleep(0.5)
		# sleep(1)
		print( chunks )
		self.assertTrue( testable.strip() == echoed )
