from covertutils.crypto.algorithms import CyclingAlgorithm

from binascii import crc32

import struct


class Crc32CyclingAlgorithm ( CyclingAlgorithm ) :

	def __crc32bytes( self, inp ) :
		try :		# Python2/3 kung fu
			res = struct.pack('<I', crc32(inp) )
		except struct.error:
			res = struct.pack('<i', crc32(inp) )

		return res


	def __produce( self, inp, feedback = 1 ) :
		assert 0 <= feedback < 4
		l = 0
		product = bytearray()
		com_inp = inp + b'\x00'
		while len(product) < self.length :
			crc = self.__crc32bytes( com_inp )
			step_length = 4 - feedback
			product += crc[:step_length]
			com_inp = com_inp[step_length:] + crc[step_length:]

		return product


	def __init__( self, message, length = 32, cycles = 10 ) :
		try :
			super( Crc32CyclingAlgorithm, self ).__init__( bytearray(message, 'utf8') )
		except TypeError :
			super( Crc32CyclingAlgorithm, self ).__init__( bytearray(message) )

		self.length = length
		self.cycles = cycles



	def digest(self) :

		call_type = type(self.message)
		result = self.message
		for c in range( self.cycles ) :
			result = self.__produce(result)[:self.length]

		return result
