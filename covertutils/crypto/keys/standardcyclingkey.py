
from covertutils.crypto.keys import CyclingKey, EncryptionKey

from covertutils.helpers import sxor

from covertutils.crypto.algorithms import StandardCyclingAlgorithm



class StandardCyclingKey( CyclingKey, EncryptionKey ) :

	# random bytes for global salting. Never transmitted.
	__salt = (
	'b2fb06410b0623bae23b5db0c43414c0ce08ae24b40808f0a25f5ca39c69bc1c'
	'1bbc9a53a91a596d2b80991aaeb644b27f46a1338024fff3f27b8db412a38691'
	'e51b80349991d50bef8baa14c5ee0b446ddbe1af122bed442d282be0c4faf1f0'
	'423269aa5fbee1349672f4f30b1362ef18e5f1b68bdba3e6062e072bea79f5f1'
	'e0848b04a5be51ebe852177ab96e4f054c40f18c3b8ec3bbae4a847a3860c3cf'
	'630e0bb327aa9dc8609e0bc9b6dbee6bd3597108f62caecf9df60acdbf8134bd'
	'7cc4457979bb54f8c7cfeb076dc843222b24cb0727b423a434f52f37a7da106a'
	'6e576e05c48223a99aafce6e9fbd24b641217662b91d060524deae84de5588c9'
	).decode('hex')


	def __init__ ( self, passphrase, cycling_algorithm = None, cycle = True, salt = None, **kw ) :
		"""
:param str passphrase: The key will be created against a `passphrase`. Passphrase will be the primary seed of all cycling. If a Secure __hash function is used, it is length won't provide additional security, or better encryption.
:param object cycling_algorithm: The cycling algorithm determines the key quality. By default the :class:CyclingAlgorithm class is used, but `hashlib.md5`, `hashlib.sha256` and every hash function object with a `digest()` method can be used.
:param str salt: Salt further differentiates the key from other keys with the same `passphrase`. For two keys to be compatible they must have the same `salt` too. If not specified a default salt is used.
		"""
		super( StandardCyclingKey, self ).__init__( passphrase, **kw )
		self.__counter = 0
		self.cycle_enabled = cycle
		self.cycling_algorithm = cycling_algorithm
		if self.cycling_algorithm == None:
			self.cycling_algorithm = StandardCyclingAlgorithm

		if salt != None :
			self.__salt = salt
		self.initial_key = self.__createKey( passphrase )
		self.reset()

		del(passphrase)	# just to be sure


	def __createKey( self, seed ) :
		return self.__hash( seed )


	def __hash( self, message ) :
		return self.cycling_algorithm ( message + self.__salt ).digest()


	def cycle( self, rounds = 1 ) :
		if self.cycle_enabled == False : return
		for i in range( rounds ) :
			self.__previous_key = self.current_key
			self.current_key = self.__hash( self.current_key )
			self.__counter += 1
		return self.current_key


	def setCycle( self, cycle ) :
		assert cycle >= 1
		d = self.__counter - cycle
		if d < 0 :
			self.cycle( -d )
		elif d > 0 :
			self.reset()
			self.cycle( cycle )


	def reset( self ) :
		self.current_key = self.initial_key
		self.cycle( 1 )
		self.__previous_key = self.initial_key
		self.__counter = 0


	def getKeyBytes( self, length = None ) :
		return self.__getKeyBytesFromKey( self.current_key, length )


	def getUUIDBytes( self, length = None ) :
		return self.__getKeyBytesFromKey( self.initial_key, length)


	def getKeyLength( self ) :
		return len(self.current_key)


	def __getKeyBytesFromKey( self, key, length = None ) :
		if None :
			numOfBytes = len(self.key)
		return key[:length]


	def xor( self, message, cycle = True ) :

		key = self.current_key
		final_key = key
		while  len(message) > len(final_key) :
			if cycle :
				self.cycle()
			final_key += self.getKeyBytes()[:2*self.getKeyLength()/3]	# 2/3 of the current key length will be used as key
		s1 = message
		s2 = final_key

		if cycle :
			self.cycle()
		ret = ''.join(sxor(a,b) for a,b in zip(s1,s2))
		# LOG.debug("XORING:\n%s\n%s\n-> %s" % (s1.encode('hex'), s2.encode('hex'), ret.encode('hex')))
		return ret


	def getCycles( self ) :
		"""
:rtype: int
:return: Returns the number of rounds the key has cycled.
		"""
		return self.__counter


	def encrypt( self, plain ) :	return self.xor( plain )
	def decrypt( self, crypt ) :	return self.xor( crypt )
