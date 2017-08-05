
from covertutils.crypto.algorithms import CyclingAlgorithm

from covertutils.helpers import sxor, permutate

from copy import deepcopy


class StandardCyclingAlgorithm ( CyclingAlgorithm ) :

	__b1 = '\x55' # 0 1 0 1  0 1 0 1
	__b2 = '\xAA' # 1 0 1 0  1 0 1 0
	__b3 = '\xf0' # 1 1 1 1  0 0 0 0
	__b4 = '\x0f' # 0 0 0 0  1 1 1 1
	__b5 = '\x3c' # 0 0 1 1  1 1 0 0
	__b6 = '\xc3' # 1 1 0 0  0 0 1 1
	__b7 = '\x1e' # 0 0 0 1  1 1 1 0
	__b8 = '\xc3' # 0 1 1 1  1 0 0 0
	__b_list = [
	__b1,
	__b2,
	__b3,
	__b4,
	__b5,
	__b6,
	__b7,
	__b8 ]

	def __init__( self, message, length = 32, cycles = 4 ) :

		super( StandardCyclingAlgorithm, self ).__init__( message )
		self.length = length
		self.cycles = cycles


	def __cycler( self, s, result, reverse = False ) :
		for c1_i, c1 in enumerate( s ) :
			mod = ( c1 + len( result ) + c1_i) % len( self.__b_list )
			if reverse :
				h1 = ord( sxor( chr(c1), self.__b_list[mod] ) )
			else :
				h1 = ord(sxor( chr(c1), self.__b_list[ (len(self.__b_list) - 1) - mod ] ) )

			if  ( h1 % 2 ) ^ reverse:
				result.insert(len( result ), h1)
			else :
				result.insert(0, h1)
		return result


	def digest( self ) :
		message = bytearray( self.message )
		prev_result = message
		message2 = deepcopy(message)

		for m in message2 :
			m2 = m / 2
			m3 = (m * 2) % 256
			message.append( m2 )

		__result = bytearray()

		for cycle in range( self.cycles + 1 ) :
			for i, c in enumerate( message ) :
				h = ( ( c**2 - 1 ) * ( len( message ) ** 2 - 1 ) * ( i ** 2 - 1 ) ) % 256
				__result.append( h )

			while len( __result ) != self.length :

				s1 = prev_result[:len( prev_result ) // 2]
				s2 = prev_result[len( prev_result ) // 2:]
				if cycle % 2 :
					s1, s2 = s2, s1

				__result = self.__cycler( s1, __result )
				__result = self.__cycler( s2, __result, True )


				d = self.length - len( __result )

				__res_temp = ''
				permut_list = []
				if d != 0 :
					for i in range( abs( d ) ) :
						c = __result[i % len(__result)]
						x = c % len( prev_result )
						permut_list.append(x)
						# print permut_list
					if d > 0 :		# need more to reach Length
						new_byte_list = permutate( prev_result, permut_list)
						new_bytes = new_byte_list
						__result.extend( new_bytes )
					else :
						__result_list = bytearray(__result)
						for x in permut_list :
							__result_list.pop( x % len(__result_list) )
							# pass
						__result = __result_list

		__str_ret = str(__result)
		return __str_ret
