import unittest

from covertutils.orchestration import StegoOrchestrator
from covertutils.datamanipulation import StegoInjector


from random import randint
from os import urandom


class Test_StegoOrchestrator( unittest.TestCase ) :


	alt_configuration = [( ('simple_alt:X','simple_alt:X'),('!H','!H'), '_data_+1' )]

	stego_conf = """
X:_data_:
Y:_data_:
Z:_data_:

simple='''4142XXXXXXXXYYYYYYYY4344'''

simple_alt='''41420000000000000000XXXX'''
	"""


	def setUp(self) :

		self.orch1 = StegoOrchestrator( "a", self.stego_conf, "simple", streams = ['main'] )
		self.orch2 = StegoOrchestrator( "a", self.stego_conf, "simple", streams = ['main'], reverse = True )

		self.orch3 = StegoOrchestrator( "a", self.stego_conf, "simple", self.alt_configuration, streams = ['main'])
		self.orch4 = StegoOrchestrator( "a", self.stego_conf, "simple", self.alt_configuration, streams = ['main'], reverse = True )


	def test_functionality( self, n = 30, l = 40 ) :

		for i in range(n) :

			ldata = randint(1,l)
			data = urandom( ldata )

			chunks = self.orch1.readyMessage( data, 'main' )
			# print chunks[0].encode('hex')

			for chunk in chunks :
				stream, message = self.orch2.depositChunk( chunk )
				# print stream, chunk, message
				assert stream != None

			# print message.encode('hex'), data.encode('hex')
			self.assertTrue( data == message )



	def test_transformation( self ) :

		data = "0"*5

		chunks = self.orch3.readyMessage( data, 'main' )
		# print chunks[0].encode('hex')

		for chunk in chunks :
			stream, message = self.orch2.depositChunk( chunk )
			# print chunk
			self.assertTrue( chunk.encode('hex')[-4:] == '4345' )	# Testing the alteration

			# print stream ,message
		self.assertTrue( data == message )




	def test_intermediate_function( self ) :


		stego_conf = """
		X:_data_:
		Y:_data_:
		Z:_data_:

		simple='''4142XXXXXXXXYYYYYYYY4344'''

		simple_alt='''41420000000000000000XXXX'''
			"""

		orch1 = StegoOrchestrator( "a", stego_conf, "simple", hex_inject = True, streams = ['main'] )
		chunks = orch1.readyMessage( "a", 'main' )

		# print chunks
