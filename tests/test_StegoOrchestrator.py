import unittest

from covertutils.orchestration import StegoOrchestrator

from covertutils.datamanipulation import StegoInjector


from random import randint
from os import urandom




def hexall( data, encode = False ) :
	if encode :
		return data.encode('hex')
	return data.decode('hex')



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

		self.orch1 = StegoOrchestrator( "a", self.stego_conf, "simple" )
		self.orch2 = StegoOrchestrator( "a", self.stego_conf, "simple", reverse = True )

		self.orch3 = StegoOrchestrator( "a", self.stego_conf, "simple", self.alt_configuration)
		self.orch4 = StegoOrchestrator( "a", self.stego_conf, "simple", self.alt_configuration, reverse = True )


	def test_functionality( self, n = 100, l = 10 ) :

		for i in range(n) :

			ldata = randint(1,l)
			data = urandom( ldata )

			chunks = self.orch1.readyMessage( data, 'main' )

			for chunk in chunks :
				stream, message = self.orch2.depositChunk( chunk )
				print stream, chunk

			# print message, data
			self.failUnless( data == message )



	def test_transformation( self ) :

		data = "0"*5

		chunks = self.orch3.readyMessage( data, 'main' )
		# print chunks[0].encode('hex')

		for chunk in chunks :
			stream, message = self.orch2.depositChunk( chunk )
			print chunk
			self.failUnless( chunk.encode('hex')[-4:] == '4345' )	# Testing the alteration

			print stream ,message
		self.failUnless( data == message )
	# 
	#
	#
	#
	# def test_intermediate_function( self ) :
	#
	# 	orch1 = StegoOrchestrator( "a", self.stego_conf, "simple", intermediate_function = hexall )
	#
	# 	chunks = orch1.readyMessage( "a", 'main' )
