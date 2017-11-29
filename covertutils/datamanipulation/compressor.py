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


	def __dummy_func( self, data ) : return data


	def compress( self, message ) :
		"""
This funtion performs all provided compression algorithm to the *message* parameter and decides which does the most efficient compression.
It does so by comparing the output lengths.

:param str message: The data to be compressed in raw bytes.
:rtype: str
:return: Data compressed by most efficient available algorithm.

"""
		if message == None :
			message = ' '
		zips = []
		for comp in self.comps :
			zfile = comp( message )
			zips.append( zfile )

		sorted_zips = sorted( zips, key = lambda tup:len( tup ) )
		winner = sorted_zips[0]
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



if __name__ == '__main__' :

	import argparse, sys, base64, binascii

	compressor = Compressor()
	parser = argparse.ArgumentParser()

	parser.add_argument("message", help = "The message to be compressed [use '-' for stdin]", type = str, default = '-' )
	parser.add_argument('--input-type', '-i', help = 'Specify the form of the input', choices = ['b64', 'hex', 'plain'], default = 'plain')
	parser.add_argument('--output-type', '-o', help = 'Specify the form of the ouput', choices = ['b64', 'hex', 'plain'], default = 'plain')
	parser.add_argument('--decompress', '-d', help = 'Add if the message is in compressed form', action = 'store_true', default = False, )
	parser.add_argument('-v', help = 'Display compression stats', action = 'store_true', default = False, )


	args = parser.parse_args()

	if args.message == '-' :
		args.message = sys.stdin.read()

	if args.input_type == 'hex' :
		message = str(binascii.unhexlify(args.message))
	elif args.input_type == 'b64' :
		message = base64.b64decode(args.message)
	else :
		message = args.message

	func = compressor.compress
	if args.decompress :
		func = compressor.decompress

	raw_res = func(message)

	res = raw_res
	if args.output_type == 'hex' :
		res = binascii.hexlify(raw_res)
	if args.output_type == 'b64' :
		res = base64.b64encode(raw_res)

	print (res)

	if args.v :
		print( "Ratio %d %% " % ( len(raw_res) / float(len(message)) * 100 ) )
