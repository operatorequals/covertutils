from covertutils.exceptions import *

from os import urandom
import logging
LOG = logging.getLogger( __name__ )

import re

from covertutils.helpers import sxor as _sxor_
from covertutils.helpers import str_similar

from copy import deepcopy


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
		# Do need the last colon (:) though.
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

	__pkt_regex = """(\w+)\s*=\s*['"]{1,3}([\w*\s]*)['"]{1,3}\s*([\[\d+:\d+\]\,[A-Z]*)"""
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
			# print pkt_name, hex_pkt, groups
			hex_pkt = re.sub("\s*",'', hex_pkt)
			# print "%s" % groups
			if groups :
				# print "Groups Found!"
				group_str_list = groups.split(',')
				group_list = []
				for group_str in group_str_list :
					if not group_str : continue
					# print "+"+group_str
					formatted_group = re.findall( self.__group_regex, group_str)[0]
					# print formatted_group
					group_list.append( formatted_group )
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
		print injection_dict
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
:return: The data extracted from the `pkt`
		"""
		extract_dict = self.__initializeDataExtraction( pkt, template )
		data = bytearray()
		print extract_dict
		for tag, value in sorted( extract_dict.iteritems() ) :
			data.extend( value )
		return str(data)


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

		for tag, functions in sorted( self.__tags.iteritems() ) :
			extr_function = functions['extr_function']
			extract_data_ = ''
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
				extract_data_ += data_byte_
				# print hex_str+"->"+data_byte_.encode('hex')
			extract_dict[tag] = bytearray( extract_data_ )
			# extract_dict[tag] = extract_data_

			# print sample_hex
			# print extract_dict.keys()
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
