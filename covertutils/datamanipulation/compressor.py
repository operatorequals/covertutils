import bz2
import zlib





class Compressor :
	"""
The Compressor class initializes the **bz2** and **zlib** compression routines.
It detects the used compression on a **trial and error** base, eliminating the need of flag bytes containing such information.
	"""


	def __init__( self ) :
		self.comps = [bz2.compress, zlib.compress, self.__dummy_func]
		self.decomps = [bz2.decompress, zlib.decompress, self.__dummy_func]

		pass

	def __dummy_func( self, data ) :
		return data


	def compress( self, message ) :
		"""
This funtion performs all provided compression algorithm to the *message* parameter and decides which does the most efficient compression.
It does so by comparing the output lengths.

:param str message: The data to be compressed in raw bytes.
:rtype: str
:return: Data compressed by most efficient available algorithm.

"""
		zips = []
		for comp in self.comps :
			zfile = comp( message )
			zips.append( zfile )
			# print len(zfile)

		sorted_zips = sorted( zips, key = lambda tup:len( tup ) )
		winner = sorted_zips[0]
		# print sorted_zips
		# print winner
		return winner


	def decompress( self, zipped ) :
		"""
This funtion performs all provided decompression algorithm to the provided data.
Based on the assumption that any decompression algorithm raises an Exception if the compressed data is not compatible, it finds the used compression algorithm and returns the decompressed data.

:param str message: The data to be compressed in raw bytes.
:rtype: str
:return: Data compressed by most efficient available algorithm.

"""

		plain = zipped
		for decomp in self.decomps :
			try :
				unzipped = decomp( zipped )
				return unzipped
			except :
				pass

		return plain
