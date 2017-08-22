import unittest


from covertutils.crypto.algorithms import *

from os import urandom
from random import randint
from entropy import shannon_entropy as entr

class TestCyclingAlgorithm(unittest.TestCase):


	def setUp( self, ) :

		self.char = 'a'
		self.entropy_floor = 0.5


	def test_entropy( self ) :
		h = StandardCyclingAlgorithm( urandom(16) ).digest()
		e = entr(str(h))
		print( "Entropy Level: %f" % e )
		self.assertTrue( e > self.entropy_floor)


	def test_consistency( self, n = 20 ) :
		for i in range(n) :
			x = urandom(16)
			h1 = StandardCyclingAlgorithm( x ).digest()
			h2 = StandardCyclingAlgorithm( x ).digest()
			self.assertTrue( h1 == h2 )


	def test_sizes( self, n = 10 ) :

		for i in range(1, n) :
			l = randint(1, n)
			x = urandom(l)
			h1 = StandardCyclingAlgorithm( x, length = i ).digest()
			# print( "Length: %d, expected Output: %d. Output: %d" % (l, i, len(h1)) )
			self.assertTrue( len(h1) == i )
