import unittest

from covertutils.orchestration import StegoOrchestrator

from covertutils.datamanipulation import StegoInjector


from random import randint
from os import urandom

class Test_StegoOrchestrator( unittest.TestCase ) :


	configuration = [( ('simple_alt:X','simple_alt:X'),('!H','!H'), '_data_+1' )]

	stego_conf = """

X:_data_:
Y:_data_:
Z:_data_:

simple='''4142XXXXXXXXYYYYYYYY4344'''


simple_alt='''41420000000000000000XXXX'''

control='''4142XXXXXXXXYYYYYYYY4344'''

	"""





	def setUp(self) :

		self.orch1 = StegoOrchestrator( "a", self.stego_conf, transformation_list = self.configuration )
		self.orch2 = StegoOrchestrator( "a", self.stego_conf, transformation_list = self.configuration, reverse = True )


	def test_functionality( self, n = 100, l = 10 ) :

		for i in range(n) :

			ldata = randint(1,l)
			data = urandom( ldata )

			chunks = self.orch1.readyMessage( data, 'simple' )
			# print chunks[0].encode('hex')
			# print chunks
			# print i

			for chunk in chunks :
				stream, message = self.orch2.depositChunk( chunk )
				self.failUnless( chunk.encode('hex')[-4:] == '4345' )	# Testing the alteration

				# print stream ,message
			# print message
			self.failUnless( data == message )




	#
	# def test_transformation( self ) :
	#
	# 	data = "0"*5
	#
	# 	chunks = self.orch1.readyMessage( data, 'simple' )
	# 	print chunks[0].encode('hex')
	#
	# 	for chunk in chunks :
	# 		stream, message = self.orch2.depositChunk( chunk )
	#
	# 		print stream ,message
	# 	self.failUnless( data == message )
