
from covertutils.crypto.algorithms import CyclingAlgorithm

from covertutils.helpers import sxor, permutate

from copy import deepcopy


class StandardCyclingAlgorithm ( CyclingAlgorithm ) :

	__b1 = b'\x55' # 0 1 0 1  0 1 0 1
	__b2 = b'\xAA' # 1 0 1 0  1 0 1 0
	__b3 = b'\xf0' # 1 1 1 1  0 0 0 0
	__b4 = b'\x0f' # 0 0 0 0  1 1 1 1
	__b5 = b'\x3c' # 0 0 1 1  1 1 0 0
	__b6 = b'\xc3' # 1 1 0 0  0 0 1 1
	__b7 = b'\x1e' # 0 0 0 1  1 1 1 0
	__b8 = b'\xc3' # 0 1 1 1  1 0 0 0

	__b_list = bytearray(
		__b1 +
		__b2 +
		__b3 +
		__b4 +
		__b5 +
		__b6 +
		__b7 +
		__b8 +
	b'')


	def __init__( self, message, length = 32, cycles = 20 ) :

		# print (len(self.__b_list))
		try :
			super( StandardCyclingAlgorithm, self ).__init__( bytearray(message, 'utf8') )
		except (TypeError, UnicodeDecodeError) :
			super( StandardCyclingAlgorithm, self ).__init__( bytearray(message) )
		self.length = length
		self.cycles = cycles


	def __cycler( self, sub_array, result, reverse = False ) :

		for c1_i in range(len(sub_array)) :
			c1 = sub_array[c1_i]
			mod = ( int(c1) + len( result) + c1_i ) % len(self.__b_list)
			if reverse :
				mod = (len(self.__b_list) - 1) - mod
			# print (c1, self.__b_list[mod])
			h1 = c1 ^ self.__b_list[mod]
			# print (h1)
			if bool(int(h1) % 2) == reverse :
				result.insert(0, h1)
			else :
				result.append(h1)
		return result


	def digest( self ) :

		message = self.message
		prev_result = message
		__result = bytearray()

		length = self.length
		cycles = self.cycles

		for cycle in range(0, cycles + 1) :

			while len( __result ) != length :

				s1 = prev_result[:len( prev_result )//2]
				s2 = prev_result[len( prev_result )//2:]
				if cycle % 2 :
					s1, s2 = s2, s1

				# print (s1, s2)
				self.__cycler(s1, __result)
				self.__cycler(s2, __result, True)
				# print ("cycled")
				# print (s1, s2)

				# print (__result)
				d = length - len( __result )
				if d == 0 :
					break

				__res_temp = bytearray()
				permut_list = []

				for i in range( abs( d ) ) :
					c = __result[i % len(__result)]
					x = c % len( prev_result )
					# print x
					permut_list.append(x)
					# print permut_list
				if d > 0 :		# need more to reach Length
					new_bytes = bytearray(permutate( prev_result, permut_list ))
					__result = __result + new_bytes
					# print new_bytes
				else :
					__result_list = bytearray(__result)
					for x in permut_list :

						__result_list.pop( x % len(__result_list) )
						# pass
					__result = bytearray(__result_list)


			prev_result = __result[:]
			portion = int((len(__result) * (float(cycle)/cycles)))
			# print (cycle, cycles)
			# print ( float(cycle)/cycles)
			# print ( portion)
			__result = __result[: portion]

		return __result
