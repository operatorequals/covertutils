import unittest

from os import urandom
from random import randint, choice
from covertutils.datamanipulation import Compressor
import string

random_bytes = urandom(64)
letters = string.ascii_letters


class Test_Compressor( unittest.TestCase ) :

	def setUp( self ) :
		self.compressor = Compressor()


	def test_consistency( self, n = 1, byte_len = 100 ) :
		for i in range( 0, n ) :
			plain = urandom( byte_len )
			zipped = self.compressor.compress( plain )

			dezip = self.compressor.decompress( zipped )
			self.assertTrue( plain == dezip )


	def test_feasibility ( self, n = 100, byte_len = 100  ):

		for i in range( 0, n ) :
			# plain = urandom( byte_len )
			plain = ''
			for i in range( byte_len ) :
				if i % 2 :
					plain += choice(random_bytes)
				else :
					plain += choice(letters)

			zipped = self.compressor.compress( plain )
			# print '%d / %d (ratio %f)' % (len(zipped), len(plain), float(len(zipped)) / len(plain))
			self.assertTrue( len(zipped) <= len(plain) )
