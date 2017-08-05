"""
This module provide classes that are relevant with Data Manipulation. Chunking, Compressing, Steganography and Alteration modules are included.
"""

from covertutils.exceptions import *

from os import urandom
from struct import pack, unpack
from copy import deepcopy

import bz2
import zlib

import re

from covertutils.helpers import sxor as _sxor_
from covertutils.helpers import str_similar


class Chunker :
	"""
The Chunker class is used to initialize chunk and de-chunk messages.

	"""

	__has_more_tag = '\x00'

	def __init__( self, chunk_length, dechunk_length = None, reverse = False ) :
		"""
:param int chunk_length: This parameter defines the size of the output chunks, containing tagging.
:param int dechunk_length: This parameter defines the size of the input chunks, containing tagging.
:param bool reverse: If `True` the `chunk_length` and `dechunk_length` are swapped. Useful when setting up 2 instances that have to match.
		"""

		self.in_length = dechunk_length
		if reverse :
			self.out_length, self.in_length = self.in_length, chunk_length

		self.tag_length = 1
		self.out_length = chunk_length - self.tag_length
		self.__message = ''


	def chunkMessage( self, payload ) :
		"""
:param str payload: The raw data to be chunked in bytes.
:rtype: list
:return: A list of chunks containing the chunked `payload`.
		"""
		chunk_size = self.out_length
		chunks = []

		for i in xrange(0, len( payload ), chunk_size) :

			chunk = payload[i:i + chunk_size]
			tag = self.__has_more_tag
			last_iteration = i + chunk_size >= len(payload)

			if last_iteration :
				padding_length = chunk_size - len(chunk)
				padding = urandom( padding_length )
				tag = chr( len(chunk) )
				# print "%s - Length %d, padding %d" % (chunk.encode('hex'), len(chunk), len(padding))
				chunk = chunk + padding

			tagged_chunk = self.__tagChunk( chunk,  tag )
			chunks.append( tagged_chunk )

		return chunks


	def deChunkMessage( self, chunk, ret_chunk = False ) :
		"""
:param str chunk: A part of a chunked message to be assembled.
:rtype: tuple
:return: The method return a tuple of (status, message). If status is `False` the provided chunk isn't the last part of the message and the message contains an empty string. Else, the assembled message can be found in `message`.

		"""
		tag, chunk = self.__dissectTag( chunk )
		# print tag
		is_last = tag != self.__has_more_tag

		if tag == '' :
			raise InvalidChunkException("Empty tag supplied to the deChunk method")
		if is_last :
			data_left = ord( tag )
			chunk = chunk [: data_left]

		self.__message += chunk
		if is_last :
			ret = self.__message
			self.reset()
			return True, ret
		if ret_chunk :
			return False, chunk
		return None, None


	def __dissectTags( self, chunks ) :
		return [ self.__dissectTag( chunk ) for chunk in chunks ]


	def __tagChunk( self, chunk, tag ) :
		return tag + chunk


	def __dissectTag( self, chunk ) :
		return chunk [:self.tag_length], chunk[self.tag_length: ]


	def reset( self ) :
		"""
Resets all partially assembled messages.
		"""
		self.__message = ''


	def chunkMessageToStr( self, payload ) :
		return ''.join(chunkMessage( payload ))




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



from os import urandom
import logging
LOG = logging.getLogger( __name__ )



class StegoInjector :
	"""
	This module provides functionality for steganography.
	It uses a configuration string with custom syntax to describe *where* and *how* will data be injected in a template.

	**Stego Configuration Syntax Description**

	* Tags
		Tags are used to specify the functions that will be applied on each byte at injection and extraction.

	* Templates
		Templates are hex strings containing the Tag Letters wherever arbitrary data can be injected.


	Example Syntax:

	.. code:: python

		# Comments symbol is traditionally the '#'

		# -- Tags --
		# Those are the tags. Declared as:
		# Letter:<InjectionFunction>:<ExtractionFunction>
		# Functions get evaluated with python 'eval' under the following context:
		# _data_: byte to be injected, extracted
		# _len_: packet length
		# _index_: index of the byte injected/extracted
		# _capacity_: Byte capacity of the packet as declared below
		# _sxor_: Function that gets 2 char bytes and returns their XOR'd value
		#
		# Data functions that are reflective [applied twice to an input returns the input (e.g XOR operation)], do not need the <ExtractionFunction> part.
		# Do need the colon (:) though.
		#
		# Examples:
		X:_data_:						# inject the data as provided
		K:_sxor_(_data_, '\\xaa'):				# inject the data xor'd with '\\xaa' byte. Use the same function for extraction
		L:chr(ord(_data_) + 1):chr(ord(_data_) - 1)		# inject each byte incremented by 1. Decrement each byte before extraction.

		# -- Packet Templates --
		# Packet Templates, declared as:
		# packet_template_name = '''Hex of the template packet with Tag Letters among the valid bytes''' []<groups>
		# Groups are declared as:
		# TagLetter[start:end]
		# and will automatically replace all bytes between 'start' and 'end' with the given Tag Letter
		#
		# Those two templates are identical (Notice the Tag Letters between the Hex Values in `ip_tcp_syn2`)
		ip_tcp_syn1 = '''450000280001000040067ccd7f0000017f00000100140050000000000000000050022000917c0000'''L[4:6],K[24:28],X[20:22]
		ip_tcp_syn2 = '''45000028LLLL000040067ccd7f0000017f000001XXXX0050KKKKKKKK0000000050022000917c0000'''

		# Whitespace and comments won't break the Strings
		mac_ip_tcp_syn = '''ffffffffffff0000000000000800	# MAC header
		450000280001000040067ccd7f0000017f000001		# IP header
		00140050000000000000000050022000917c0000'''K[18:20],K[38:42],K[34:36]
	"""
	__comment_sign = '#'

	__pkt_regex = """(\w+)\s*=\s*['"]{1,3}([\w*\s]*)['"]{1,3}\s*([\[\d+\:\d+\]\w,]*?)"""
	__tag_regex = '([A-Za-z]+):(.*?):(.*)]?'
	__data_regex = '[\s(]+_data_[,\s\.)]+'
	__group_regex = '([A-Za-b])\[(\d+)+:(\d+)\]'

	__comment_regex = '%s.*' % __comment_sign

	__not_permitted_chars = '1234567890ABCDEF'
	__tag_chars = ''


	def __init__( self, stego_template ) :

		self.__tags, self.__packets = self.__parseStegoScheme( stego_template )
		# print self.__packets

	def __parseStegoScheme( self, stego_template ) :

		#	Remove comments
		stego_template = re.sub( self.__comment_regex,'',stego_template )

		tags = re.findall( self.__tag_regex, stego_template )

		tag_dict = {}
		for tag, inj_function, extr_function in tags :

			tag = tag.upper()
			# print tag, function
			if len(tag) != 1 :
				raise StegoSchemeParseException( "MultiCharacter Tags are not allowed. Redefine '%s'" % tag )

			if tag in self.__not_permitted_chars :
				raise StegoSchemeParseException( "Tag '%s' is a Letter used in Hex. Tags must be different from 'ABCDEF'" % tag )

			if tag in tag_dict.keys() :
				raise StegoSchemeParseException( "Tag '%s' is already defined." % tag )

			inj_function = '(%s)' % inj_function
			extr_function = '(%s)' % extr_function
			if extr_function == '()' :
				extr_function = inj_function

			f_match = re.findall( self.__data_regex, inj_function )

			if not f_match :
				raise StegoSchemeParseException( "Injection function for Tag: '%s' does not contain '_data_' keyword" % tag )

			f_match = re.findall( self.__data_regex, extr_function )
			if not f_match :
				raise StegoSchemeParseException( "Extraction function for Tag: '%s' does not contain '_data_' keyword" % tag )

			# print tag, function
			LOG.debug("Adding tag '%s' with Data Functions: < %s > : < %s >" % (tag, inj_function, extr_function))
			tag_dict[tag] = {
								"inj_function": inj_function,
								"extr_function": extr_function
							}

		pkt_dict = {}

		pkt_list = re.findall( self.__pkt_regex, stego_template)
		for pkt_name, hex_pkt, groups in pkt_list :
			hex_pkt = re.sub("\s*",'', hex_pkt)
			group_list = []
			if groups :	# the groups Regex part returned something, handle the groups
				for group_str in group_list :
					group_list.append( re.findall( self.__group_regex, group_str)[0] )
				hex_pkt = self.__applyGroups( hex_pkt, group_list, tag_dict.keys())

			if self.__checkPermittedChars( hex_pkt, tag_dict.keys() ) :


				cap = self.__getCapacityDict( hex_pkt , tag_dict.keys() )
				pkt_dict[ pkt_name ] = ( hex_pkt, cap )

		return tag_dict, pkt_dict


	def getTemplates( self ) :
		return self.__packets.keys()


	def getCapacityDict( self, template ) :
		"""
:param str template: The name of the template whose capacity dict is desired.
:rtype: dict
:return: The template's capacity dict containing Tag Letters as keys and capacity of each Tag in bytes as values.

A sample  *configuration* :

.. code:: python

	X:_data_:
	Y:_data_:
	sample='''4141XX4242YYYY'''

Example ::

	psi = StegoInjector( configuration )
	psi.getCapacityDict( 'sample1' )
	{ 'X' : 1, 'Y' : 2 }

		"""
		return self.__packets[template][1]


	def getCapacity( self, template, tag = None ) :
		"""
:param str template: The name of the template whose capacity is desired.
:rtype: int
:return: The template's capacity in bytes
		"""
		return sum(self.__packets[template][1].values())


	def __getCapacityDict( self, pkt, tag_chars ) :
		caps = {}
		for tag in tag_chars :
			caps[tag] = pkt.count(tag) / 2 	# in bytes
		return caps


	def __checkPermittedChars( self, pkt, tag_chars ) :
		for c in pkt :
			c = c.upper()
			if c not in self.__not_permitted_chars and c not in tag_chars :
				raise StegoSchemeParseException( "Char '%s' in Packet '%s' is not Hex Digit nor Tag" % (c, pkt) )
				return False
		return True


	def __applyGroups( self, pkt, groups, tag_chars ) :
		group_str = '%s[%d, %d]'
		pkt = bytearray(pkt)
		for tag, start, end in groups :
			start = int(start)
			end = int(end)
			group_repr = group_str % (tag, start, end)
			if tag not in tag_chars :
				raise StegoSchemeParseException( "Group Tag '%s' in Group: '%s' is not defined." % (tag, group_repr) )
			if start > end :
				raise StegoSchemeParseException( "Starting byte is greater than Ending Byte in Group %s" % group_repr)
			for hex_index in xrange(0, len( pkt ), 2) :
				byte_index = hex_index / 2
				# print hex_index, byte_index
				if byte_index >= start and byte_index < end :
					pkt[ hex_index ] = tag
					pkt[ hex_index + 1] = tag
		# print pkt
		return str(pkt)


	def __blankifyPacketFields( self, pkt, sample ) :
		for i in range(len(sample)) :
			char = chr(sample[i])
			if char in self.__tags.keys() :
				pkt[i] = sample[i]
		return pkt


	def injectByTag( self, data_dict, template, pkt = None ) :
		"""
:param dict data_dict: The data to be injected in a dict format, with *Tag Letters* as keys and Data to be injected where the specific Tag Letters are placed, as values.
:param str template: The template that will be used to inject the data into.
:param str pkt: A packet that matches the template is size, to inject the data instead of the template. A copy of the template will be used if this argument is not provided.
:rtype: str
:return: Template or packet with the given data injected.

A sample  *configuration* :

.. code:: python

	X:_data_:
	Y:_data_:
	sample='''4141XX4242YY'''

Example ::

	data_dict = { 'X' : '0', 'Y' : 1 }
	psi = StegoInjector( configuration )
	psi.injectByTag( data_dict, 'sample1' )
	'AA0BB1'

		"""
		data_len = len( ''.join(data_dict.values()) )
		pkt, sample_capacity = self.__initializeInjection( data_len, template, pkt )

		injection_dict = data_dict

		pkt = self.__injectFromDict( pkt, injection_dict )
		pkt = str( pkt ).decode('hex')

		# print pkt
		# print injection_dict
		return pkt


	def inject( self, data, template, pkt = None ) :
		"""
:param str data: The data to be injected in raw bytes
:param str template: The template that will be used to inject the data into.
:param str pkt: A packet that matches the template is size, to inject the data instead of the template. A copy of the template will be used if this argument is not provided.
:rtype: str
:return: Template or packet with the given data injected.
		"""
		data_len = self.getCapacity( template )
		pkt, sample_capacity = self.__initializeInjection( data_len, template, pkt )

		injection_dict = self.__createInjectionDict( pkt, data, sample_capacity )

		pkt = self.__injectFromDict( pkt, injection_dict )
		pkt = str( pkt ).decode('hex')

		# print injection_dict
		return pkt


	def __initializeInjection( self, data_len, template, pkt = None ) :

		sample_packet  = self.__packets[ template ][0]
		sample_capacity = self.getCapacity( template )

		if pkt == None :
			pkt = deepcopy( sample_packet )			# COPY DEEPLY
		else :
			pkt = pkt.encode('hex')


		if data_len != sample_capacity :
			raise StegoDataInjectionException( "Incompatible Data Lengths. Packet is capable of %d bytes, %d bytes given" % ( sample_capacity, data_len ) )

		sample = bytearray( sample_packet )
		pkt = bytearray( pkt )
		# print sample
		# print pkt
		# print len(sample), len(pkt)

		if len(sample) != len(pkt) :
			raise StegoDataInjectionException( "Given packet has not the same length with the Sample." )

		if pkt != sample :
			pkt = self.__blankifyPacketFields(pkt, sample, )

		return pkt, sample_capacity


	def __createInjectionDict( self, pkt, data, sample_capacity ) :
		data = bytearray(data)
		injection_dict = {}
		for hex_index in xrange( 0, len(pkt), 2 ) :
			if not data :
				continue
			data_to_inj = chr( data[0] )
			tag, data_byte_ = self.__injectInOffset( hex_index, pkt, sample_capacity, data_to_inj )

			if tag == None :
				continue

			if tag not in injection_dict.keys() :
				injection_dict[ tag ] = bytearray()
			data.pop(0)
			injection_dict[ tag ] += data_byte_
			data_byte_ = ''
		return injection_dict


	def __injectFromDict( self, pkt_hex, injection_dict ) :
		for tag, data in injection_dict.items() :
			data = bytearray(data)
			while data :
				data_byte = data.pop(0)
				hex_byte = chr(data_byte).encode('hex')

				hex1_index = pkt_hex.index( tag )
				pkt_hex[ hex1_index ] = hex_byte[0]

				hex2_index = pkt_hex.index( tag )
				pkt_hex[ hex2_index ] = hex_byte[1]
		return pkt_hex


	def __injectInOffset( self, hex_index, pkt_hex, sample_cap, data_to_inj ) :
			byte_index = hex_index / 2
			tag = chr( pkt_hex[hex_index] )
			if tag not in self.__tags.keys() :
				return None, None
			else :
				inj_function = self.__tags[ tag ]['inj_function']

#	============== Eval Environment ======
			_len_ = len(pkt_hex)
			_index_ = byte_index
			_data_ = data_to_inj
			_capacity_ = sample_cap
			evaled = eval( inj_function )
#	======================================
			# print hex_index, evaled
			return tag, evaled


	def extract( self, pkt, template ) :
		"""
:param str pkt: A packet that matches the template in size, that contains covert data the way the `template` provides.
:param str template: The template that will be used to extract the data from. It must be the same with the one used to inject the data in the `pkt`.
:rtype: str
:return: The data exatrcted from the `pkt`
		"""
		extract_dict = self.__initializeDataExtraction( pkt, template )
		data = ''.join( extract_dict.values() )
		return data


	def extractByTag( self, pkt, template ) :
		return self.__initializeDataExtraction( pkt, template )


	def __initializeDataExtraction( self, pkt, template ) :

		extract_dict = {}
		pkt_hex = pkt.encode( 'hex' )
		sample_hex, sample_cap = self.__packets[ template ]
		data = ''
		sample_hex = bytearray(sample_hex)

		# print len(sample_hex), len(pkt_hex)
		if len(sample_hex) != len(pkt_hex) :
			raise StegoDataExtractionException("Given packet and Sample packet have not the same length")

		for tag, functions in self.__tags.iteritems() :
			extr_function = functions['extr_function']
			extract_dict[tag] = ''
			while tag in sample_hex :
				tag_index = sample_hex.index( tag )
				hex1 = pkt_hex[ tag_index ]
				sample_hex[ tag_index ] = '~'	# Remove the Tag

				tag_index = sample_hex.index( tag )
				hex2 = pkt_hex[ tag_index ]
				sample_hex[ tag_index ] = '~'	# Remove the Tag
				hex_str = hex1 + hex2

				raw_byte_ = hex_str.decode('hex')
				data_byte_ = self.__eval_environ\
							( raw_byte_, extr_function, len(pkt), tag_index, sample_cap )
				extract_dict[ tag ] += data_byte_
				# print hex_str+"->"+data_byte_.encode('hex')

			# print sample_hex

		return extract_dict


	def __eval_environ( self, _data_, function, _len_, _index,_capacity_ ) :
#	============== Eval Environment ======
		return eval( function )
#	======================================


	def __extractFromOffset( self, hex_index, pkt, sample_hex, sample_cap ) :
		byte_index = hex_index/2
		hex_digit = sample_hex[ hex_index ]
		if hex_digit not in self.__tags.keys() :
			return None, None

		extr_function = self.__tags[ hex_digit ]['extr_function']
#	============== Eval Environment ======
		_len_ = len(pkt)
		_index_ = byte_index
		_data_ = pkt[ byte_index ]
		_capacity_ = sample_cap
		data_byte_ = self.__eval_environ( _data_, extr_function, _len_, _index,_capacity_)
#	======================================
		return hex_digit, data_byte_


	def guessTemplate( self, pkt ) :
		"""
This method tries to guess the used template of a data packet by computing similarity of all templates against it.

:param str pkt: The data packet whose template is guessed.
:rtype: str
:return: A tuple containing the template name that matches best with the given packets and the similarity ratio.

		"""
		ret = []
		for template in self.__packets.keys() :
			cap = self.getCapacity( template )
			payload = urandom( cap )
			pkt_test = self.inject( payload, template )
			if len( pkt_test ) != len( pkt ) :
				continue
			sim_ratio = str_similar( pkt, pkt_test )
			ret.append( ( template, sim_ratio ) )

		winner = sorted( ret, key = lambda tup:tup[1] )[-1]
		return winner



def asciiToHexTemplate( pkt, marker = '~', substitute = 'X' ) :
	"""
This module function converts an ASCII chunk with single-byte `markers` and returns a `template`.

:param str pkt: The data packet in ASCII with `marker` byte where arbitrary bytes can be injected.
:param str marker: The byte that will be interpreted as `marker`
:param str substitute: The byte that will be replace the marker bytes in the hex-`template` representation.
:rtype: str
:return: The template representation populated with the `substitute` wherever the `marker` byte was placed.

Example:

.. code:: python

	req = 'GET /search.php?q=~~~~~~~~\\n\\n'
	template = asciiToHexTemplate( req )
	print template
	474554202f7365617263682e7068703f713dXXXXXXXXXXXXXXXX0a0a


"""
	marker_hex = marker.encode('hex')
	pkt_hex = pkt.encode('hex')
	pkt_hex_spaced = ' '.join([ "%s%s" % ( pkt_hex[i], pkt_hex[i+1] )
						for i in range( 0, len(pkt_hex) - 1, 2) ])
	pkt_hex_spaced = pkt_hex_spaced.replace( marker_hex, substitute * 2 )
	return pkt_hex_spaced.replace(' ', '')




class DataTranformer :
	"""
This class provides automated data transformations.
It uses the :class:`coverutils.datamanipulation.StegoInjector` class to create alterations to existing data chunks.

**Transformation List**

The Transformation List argument is a specially structured list to dictate to the `DataTranformer` which changes should be done to data packet.
Specifically, for a SYN - (RST, ACK) sequence to be simulated, the following configuration should be used:

.. code:: python

	X:_data_:
	L:_data_:
	K:_data_:

	ip_tcp_syn = '''45000028LLLL000040067ccd7f0000017f000001XXXX0050KKKKKKKK0000000050022000917c0000'''

	ip_tcp_rst_ack = '''450000280001000040067ccd7f0000017f0000010014005000000000XXXXXXXXXX50142000916a0000'''

The Transformation List that has to be used should dictate the class to:

 - Unpack Sequence Number from `ip_tcp_syn` template (K tag)
 - Increment it by 1
 - Place it to a `ip_tcp_rst_ack` template (X tag)
 - All the above while handling **endianess**, **integer overflow checks**, etc

The `transformation_list` is declared below:

.. code:: python

	transformation_list = [ (	# Tranformation #1
		( 'ip_tcp_syn:K', 'ip_tcp_rst_ack:X' ),		# From template:tag to template:tag
		('!I','!I')		# Unpack as an 4-byte Integer (reverse Endianess as of network Endianess) and pack it to 4-byte Integer (reverse Endianess again)
		'_data_ + 1'	# Eval this string (with the extracted/unpacked data as '_data_') and pack the result.
		),
			# No other transformations
	]

"""
	def __init__( self, stego_configuration, transformation_list ) :
		"""
:param str stego_configuration: The Stego Configuration to initialize the internal :class:`covertutils.datamanipulation.StegoInjector` object.
:param list transformation_list: The Tranformation List as described above.

		"""
		self.injector = StegoInjector( stego_configuration )
		self.transformation_list = transformation_list


	def runAll( self, pkt, template ) :
		"""
Runs all Tranformations in the `transformation_list` that relate with the specified template.

:param str pkt: The data packet to run the Tranformations on. In `Raw Bytes`.
:param str template: The template string that describes the given data packet.
:rtype: str
:return: Returns the `pkt` with all the related tranformations applied.
		"""

		for trans_tuple in self.transformation_list :

			templates, struct_strs, eval_str = trans_tuple
			(out_template_tag, in_template_tag) = templates
			out_template, out_tag = out_template_tag.split(':')
			in_template, in_tag = in_template_tag.split(':')
 			(out_struct, in_struct) = struct_strs

			if template != out_template :
				continue

			out_data = self.injector.extractByTag( pkt, template )[ out_tag ]
			structed_data = unpack( out_struct, out_data )[0]
			_data_ = structed_data
			output_data = eval( eval_str )
			injectable_data = pack( in_struct, output_data )
			injectable_dict = {'X' : injectable_data}
			# print injectable_data.encode('hex')
			# print self.injector.getCapacity( template ), len( injectable_data)
			pkt = self.injector.injectByTag( injectable_dict, template, pkt  )


		return pkt
