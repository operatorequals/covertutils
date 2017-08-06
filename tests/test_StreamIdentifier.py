import unittest

from os import urandom
from random import randint
from covertutils.orchestration import StreamIdentifier

from random import choice


from hashlib import sha512

class TestStreamIdentifier( unittest.TestCase ) :

	def setUp( self,
		streams = ["main", 'shellcode', 'control']) :

		passp = urandom(10)
		# passp = 'pass'

		self.id_1 = StreamIdentifier( passp,
								stream_list = streams,
								cycling_algorithm = sha512
								 )
		self.id_2 = StreamIdentifier( passp,
								stream_list = streams,
								cycling_algorithm = sha512,
								reverse = True
								)

		for s in ( 'easy', 'medium', 'hard' ) :
			self.id_2.addStream(s)
			self.id_1.addStream(s)

		self.streams = self.id_1.getStreams()
		self.streams.remove('control')


	def testGuess( self, n = 100 ) :
		idents = (self.id_1, self.id_2)

		for i in range(n) :
			chosen = randint(1, 100) % 2
			checker = 1 - chosen
			ident1 = idents[chosen]
			ident2 = idents[checker]
			stream = choice ( self.streams )
			tag = ident1.getIdentifierForStream( stream, 2 )

			guess = ident2.checkIdentifier(tag)

			print( "%s) Tagger:%d. [%s] - %s > %s" % ( i, chosen, stream, guess, tag.encode('hex') ) )
			self.assertTrue( stream == guess )
