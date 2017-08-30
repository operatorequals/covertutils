from abc import ABCMeta, abstractmethod

from covertutils.datamanipulation import Chunker
from covertutils.datamanipulation import Compressor

from covertutils.crypto.keys import StandardCyclingKey
from covertutils.crypto.algorithms import StandardCyclingAlgorithm

from covertutils.orchestration import StreamIdentifier


from string import ascii_letters
from copy import deepcopy



class Orchestrator :
	"""
Orchestrator objects utilize the `raw data` to **(stream, message)** tuple translation and vice-versa.
**(stream, message)** tuples are recognised by the classes in :mod:`covertutils.handlers` but data transmission is only possible with `raw data`.


	"""
	# __metaclass__ = DocABCMeta
	__metaclass__ = ABCMeta

	__pass_encryptor = ascii_letters * 10

	def __init__( self, passphrase, tag_length, cycling_algorithm = None, streams = ['control'], reverse = False ) :
		self.compressor = Compressor()

		self.cycling_algorithm = cycling_algorithm
		if self.cycling_algorithm == None:
			self.cycling_algorithm = StandardCyclingAlgorithm

		passGenerator = StandardCyclingKey( passphrase, cycling_algorithm = self.cycling_algorithm )
		pass1 = passGenerator.encrypt( self.__pass_encryptor )
		pass2 = passGenerator.encrypt( self.__pass_encryptor )
		pass3 = passGenerator.encrypt( self.__pass_encryptor )


		self.encryption_key = StandardCyclingKey( pass2, cycling_algorithm = self.cycling_algorithm )
		self.decryption_key = StandardCyclingKey( pass3, cycling_algorithm = self.cycling_algorithm )

		if reverse :
			self.encryption_key, self.decryption_key = self.decryption_key, self.encryption_key

		self.reverse = reverse

		self.streamIdent = StreamIdentifier( pass1, reverse = reverse, stream_list = streams, cycling_algorithm = self.cycling_algorithm )

		self.default_stream = self.streamIdent.getHardStreamName()
		if self.default_stream not in streams :
			streams.insert( 0, self.default_stream )

		self.streams_buckets = {}
		for stream in streams :
			self.addStream( stream )

		self.tag_length = tag_length


	def deleteStream( self, stream ) :
		self.streamIdent.deleteStream( stream )
		del self.streams_buckets[ stream ]


	def addStream( self, stream ) :
		if stream not in self.streamIdent.getStreams() :
			self.streamIdent.addStream( stream )

		self.streams_buckets[ stream ] = {}
		self.streams_buckets[ stream ]['message'] = ''
		self.streams_buckets[ stream ]['chunker'] = None


	def getChunkerForStream( self, stream ) :
		chunker = self.streams_buckets[ stream ]['chunker']
		return chunker



	def getStreamDict( self ) :
		d = deepcopy(self.streams_buckets)
		for stream in self.streams_buckets.keys() :
			d[stream] = d[stream]['message']
		return d


	def getStreams( self ) :
		return self.streams_buckets.keys()


	def getDefaultStream( self ) :
		"""
This method returns the stream that is used if no stream is specified in `readyMessage()`.

:rtype: str
		"""
		return self.default_stream


	def reset( self ) :
		"""
This method resets all components of the `Orchestrator` instance, effectively restarting One-Time-Pad keys, etc.
		"""
		self.encryption_key.reset()
		self.decryption_key.reset()
		self.streamIdent.reset()


	def getStreams( self ) :
		return self.streams_buckets.keys()


	def __dissectTag( self, chunk ) :
		return chunk[-self.tag_length:], chunk[:-self.tag_length]


	def __addTag( self, chunk, tag ) :
		return chunk + tag


	def readyMessage( self, message, stream = None ) :
		"""
:param str message: The `message` to be processed for sending.
:param str stream: The `stream` where the message will be sent. If not specified the default `stream` will be used.
:rtype: list
:return: The raw data chunks translation of the `(stream, message)` tuple.
		"""
		if stream == None :
			stream = self.default_stream
		message = self.compressor.compress( message )

		chunker = self.getChunkerForStream( stream )
		chunks = chunker.chunkMessage( message )
		ready_chunks = []
		for chunk in chunks :
			tag = self.streamIdent.getIdentifierForStream( stream,
														byte_len = self.tag_length )
			encr_chunk = self.encryption_key.xor( chunk )

			ready = self.__addTag(encr_chunk, tag)
			ready_chunks.append( ready )

		return ready_chunks


	def depositChunk( self, chunk, ret_chunk = False ) :
		"""
:param str chunk: The raw data chunk received.
:param bool ret_chunk: If `True` the message part that exists in the chunk will be returned. Else `None` will be returned, unless the provided chunk is the last of a message.
:rtype: tuple
:return: The `(stream, message)` tuple.
		"""
		tag, chunk = self.__dissectTag( chunk )
		stream = self.streamIdent.checkIdentifier( tag )
		if stream == None :
			return None, None

		chunker = self.getChunkerForStream( stream )
		decr_chunk = self.decryption_key.xor( chunk )
		status, message = chunker.deChunkMessage( decr_chunk )
		if status :
			message = self.compressor.decompress( message )
			self.streams_buckets[ stream ]['message'] = message
			return stream, message
		return stream, None
