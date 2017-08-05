
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

	def __init__( self, message, length = 32, cycles = 20 ) :

		super( StandardCyclingAlgorithm, self ).__init__( message )
		self.length = length
		self.cycles = cycles


	# def __cycler( self, s, result, reverse = False ) :
	# 	for c1_i, c1 in enumerate( s ) :
	# 		mod = ( c1 + len( result ) + c1_i) % len( self.__b_list )
	# 		if reverse :
	# 			h1 = ord( sxor( chr(c1), self.__b_list[mod] ) )
	# 		else :
	# 			h1 = ord(sxor( chr(c1), self.__b_list[ (len(self.__b_list) - 1) - mod ] ) )
	#
	# 		if  ( h1 % 2 ) ^ reverse:
	# 			result.insert(len( result ), h1)
	# 		else :
	# 			result.insert(0, h1)
	# 	return result


	def digest( self ) :

		message = self.message
		prev_result = message
		__result = ''

		length = self.length
		cycles = self.cycles

		for cycle in range(0, cycles + 1) :

			while len( __result ) != length :

				s1 = prev_result[:len( prev_result )/2]
				s2 = prev_result[len( prev_result )/2:]
				if cycle % 2 :
					s1, s2 = s2, s1

				for c1_i in range(len(s1)) :
					c1 = s1[c1_i]
					mod = (ord(c1) + len( __result) + c1_i) % 6
					h1 = sxor( c1, self.__b_list[mod] )
					if ord(h1) % 2 :
						__result = h1 + __result
					else :
						__result = __result + h1

				for c2_i in range(len(s2)) :
					c2 = s2[c2_i]
					mod = (ord(c2) + len( __result ) + c2_i) % 6
					h2 = sxor( c2, self.__b_list[ (len(self.__b_list) - 1) - mod ] )
					if ord(h2) % 2 :
						__result = __result + h2
					else :
						__result = h2 + __result


				d = length - len( __result )

				__res_temp = ''
				permut_list = []
				if d != 0 :
					for i in range( abs( d ) ) :
						c = __result[i % len(__result)]
						x = ord(c) % len( prev_result )
						# print x
						permut_list.append(x)
						# print permut_list
					if d > 0 :		# need more to reach Length
						new_byte_list = permutate( prev_result, permut_list)
						new_bytes = ''.join(new_byte_list)
						__result = __result + new_bytes
						# print new_bytes
					else :
						__result_list = bytearray(__result)
						for x in permut_list :

							__result_list.pop( x % len(__result_list) )
							# pass
						__result = str(__result_list)


			prev_result = __result[:]
			portion = int((len(__result) * (float(cycle)/cycles)))
			__result = __result[: portion]

		return __result
