from covertutils.exceptions import *

from os import urandom


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
