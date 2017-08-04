import unittest


from covertutils.crypto.keys import *

from os import urandom
from random import randint
from entropy import shannon_entropy as entr

class TestKeys(unittest.TestCase) :


	plaintext = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum"

	def setUp( self ) :
		pass



	def test_cycle_consistent( self, n = 10 ) :

		n = n*2
		pass_ = urandom( n )
		k1 = StandardCyclingKey( pass_ )

		k1.setCycle( n )
		self.failUnless( n == k1.getCycles() )
		nth_key = k1.getKeyBytes()
		k1.reset()
		k1.cycle( n/2 )
		self.failUnless( n/2 == k1.getCycles() )
		k1.cycle( n/2 )

		nth_key_2 = k1.getKeyBytes()

		self.failUnless( nth_key == nth_key_2 )


	def test_random_passphrase( self, n = 4 ) :

		k1 = StandardCyclingKey( urandom(n) )
		k2 = StandardCyclingKey( urandom(n) )

		crypt1 = k1.xor(self.plaintext)
		crypt2 = k2.xor(self.plaintext)

		self.failUnless( crypt1 != crypt2 )


	def test_correct_passphrase( self, n = 64 ) :

		pass_ = urandom( n )
		k1 = StandardCyclingKey( pass_ )
		k2 = StandardCyclingKey( pass_ )

		crypt1 = k1.xor(self.plaintext)
		plain = k2.xor(crypt1)
		# print plain[-10:], self.plaintext[-10:]
		self.failUnless( plain == self.plaintext )
