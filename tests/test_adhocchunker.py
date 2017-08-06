import unittest

from os import urandom
from random import randint, choice
from covertutils.datamanipulation import AdHocChunker
import string

random_bytes = urandom(64)
letters = string.ascii_letters

class Test_AdHocChunker( unittest.TestCase ) :

	def setUp( self ) :
		self.c = AdHocChunker()



	def test_chunkConsistency( self, n = 519, size = 514 ) :

		for i in range( 5, n ) :
			# print i
			data = urandom(i)
			chunks = self.c.chunkMessage( data, size )
			for chunk in chunks :
				# print chunk.encode('hex'), len(chunk)
				self.assertTrue( len(chunk) == size )



	def test_deChunkConsistency( self, n = 514, size = 10 ) :

		for i in range( 2, n ) :
			# print i
			# data = urandom(i)
			data = "A"*i
			# print "Data: %s" % data.encode('hex')
			chunks = self.c.chunkMessage( data, size )
			for chunk in chunks :
				# print "Chunk: %s" % chunk.encode('hex')
				status, ret = self.c.deChunkMessage( chunk )
			# print  data.encode('hex'), ret.encode('hex'), len(ret)
			self.assertTrue( data == ret )
