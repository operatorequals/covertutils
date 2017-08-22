from covertutils.crypto.algorithms import CyclingAlgorithm

from binascii import crc32

from struct import pack


class NullCyclingAlgorithm ( CyclingAlgorithm ) :

	def __init__( self, message, length = 32, cycles = 10  ) :
		super( NullCyclingAlgorithm, self ).__init__( message )
		self.length = length

	def digest( self ) :
		return b'\x00'*self.length
