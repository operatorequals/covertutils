import unittest

from os import urandom
from random import randint, choice
from string import ascii_letters
from covertutils.datamanipulation import Compressor

random_bytes = urandom(64)
try:
	letters = bytes(ascii_letters, encoding='utf8')  # Python 3
except TypeError:
	letters = bytes(ascii_letters)                   # Python 2


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
			plain = bytearray()
			for i in range( byte_len ) :
				if i % 2 :
					plain.append( choice( random_bytes ) )
				else :
					plain.append( choice( letters ) )

			plain = bytes( plain )
			zipped = self.compressor.compress( plain )
			# print '%d / %d (ratio %f)' % (len(zipped), len(plain), float(len(zipped)) / len(plain))
			self.assertTrue( len(zipped) <= len(plain) )
