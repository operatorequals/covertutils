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
		self.assertTrue( n == k1.getCycles() )
		nth_key = k1.getKeyBytes()
		k1.reset()
		k1.cycle( n/2 )
		self.assertTrue( n/2 == k1.getCycles() )
		k1.cycle( n/2 )

		nth_key_2 = k1.getKeyBytes()

		self.assertTrue( nth_key == nth_key_2 )


	def test_random_passphrase( self, n = 4 ) :

		k1 = StandardCyclingKey( urandom(n) )
		k2 = StandardCyclingKey( urandom(n) )

		crypt1 = k1.xor(self.plaintext)
		crypt2 = k2.xor(self.plaintext)

		self.assertTrue( crypt1 != crypt2 )


	def test_correct_passphrase( self, n = 64 ) :

		pass_ = urandom( n )
		k1 = StandardCyclingKey( pass_ )
		k2 = StandardCyclingKey( pass_ )

		crypt1 = k1.xor(self.plaintext)
		plain = k2.xor(crypt1)
		# print plain[-10:], self.plaintext[-10:]
		self.assertTrue( plain == self.plaintext )


	def test_small_char( self, n = 32 ) :

		data = 'a'
		pass_ = urandom( n )
		k1 = StandardCyclingKey( pass_ )
		k2 = StandardCyclingKey( pass_ )

		encrypted_list = []
		for i in range( n ) :
			# print k1.getCycles(), k1.getKeyBytes().encode('hex')
			encr = k1.encrypt( data )
			# print encr.encode('hex')
			encrypted_list.append( encr )
		encrypted = set (encrypted_list)
		self.assertTrue( len(encrypted) > 1)

		print
		for encr in encrypted_list :
			# print k2.getCycles(), k2.getKeyBytes().encode('hex')
			decr = k2.decrypt( encr )
			# print encr.encode('hex')

			self.assertTrue( decr == 'a' )


	def test_not_cycling( self ) :
		k1 = StandardCyclingKey( "pass", cycle = False )
		message = "A" * 16
		ctext1 = k1.encrypt( message )
		ctext2 = k1.encrypt( message )


		ctext3 = k1.encrypt( message*32 )
		ctext4 = k1.encrypt( message*32 )
		# print ctext1.encode('hex')
		# print ctext2.encode('hex')
		self.assertTrue( ctext2 == ctext1 )

		self.assertTrue( ctext3 == ctext4 )
