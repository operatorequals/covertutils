from covertutils.exceptions import *

from os import urandom

from struct import pack, unpack

class AdHocChunker :
	"""
The Chunker class is used to initialize chunk and de-chunk messages.

	"""

	def __init__( self, tag_length = 2 ) :
		"""
		"""
		self.__message = ''
		self.tag_length = tag_length
		self.reset()

	def chunkMessage( self, payload, chunk_size = 10 ) :
		"""
:param str payload: The raw data to be chunked in bytes.
:rtype: list
:return: A list of chunks containing the chunked `payload`.
		"""
		data = self.__prepareMessage( payload )
		chunks = []
		while data :

			if len(data) >= chunk_size :
				chunk = data[:chunk_size]
				data = data[chunk_size:]
				# print len(data)
			else :
				chunk = data
				padding_length = chunk_size - len(chunk)
				chunk += urandom( padding_length )
				chunks.append( chunk )
				break

			chunks.append( chunk )
		return chunks


	def deChunkMessage( self, chunk ) :
		"""
:param str chunk: A part of a chunked message to be assembled.
:rtype: tuple
:return: The method return a tuple of (status, message). If status is `False` the provided chunk isn't the last part of the message and the message contains an empty string. Else, the assembled message can be found in `message`.

		"""
		if self.remaining_bytes == 0 :
			tag, data = self.__dissectTag( chunk )
			self.remaining_bytes = self.__decodeTag( tag )

		else :
			data = chunk

		data_length = len(data)

		if data_length <= self.remaining_bytes :
			self.__message += data
			self.remaining_bytes -= data_length
		else :
			self.__message += data[:self.remaining_bytes]
			self.remaining_bytes = 0

		if self.remaining_bytes == 0 :
			ret = self.__message
			self.reset()
			return True, ret
		return None, None

	def __decodeTag( self, tag ) :
		while len(tag) < 8 :
			tag = '\x00' + tag
		return unpack(">Q", tag)[0]


	def __prepareMessage( self, payload ) :
		data = payload
		data_length = len(data)
		tag = self.__createTag( data )
		data = tag + data
		return data


	def __createTag( self, chunk ) :
		data_length = len(chunk)
		tag = pack(">Q", data_length )	# Q: 8 bytes - unsigned long long - huge number
		while tag[0] == '\x00' and len(tag) > self.tag_length :
			tag = tag[1:]
		return tag

	def __dissectTags( self, chunks ) :
		return [ self.__dissectTag( chunk ) for chunk in chunks ]


	def __tagChunk( self, chunk, tag ) :
		return tag + chunk


	def __dissectTag( self, chunk ) :
		tag = chunk[:self.tag_length]
		chunk = chunk[self.tag_length:]
		return tag, chunk


	def reset( self ) :
		"""
Resets all partially assembled messages.
		"""
		self.__message = ''
		self.remaining_bytes = 0


	def chunkMessageToStr( self, payload ) :
		return ''.join(chunkMessage( payload ))
