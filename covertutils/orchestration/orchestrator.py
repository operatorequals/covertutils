from abc import ABCMeta, abstractmethod

from covertutils.datamanipulation import Chunker
from covertutils.datamanipulation import Compressor

from covertutils.crypto.keys import StandardCyclingKey
from covertutils.crypto.algorithms import StandardCyclingAlgorithm

from covertutils.orchestration import StreamIdentifier

from covertutils.helpers import xor_str

from string import ascii_letters
from copy import deepcopy



class Orchestrator :
	"""
Orchestrator objects utilize the `raw data` to **(stream, message)** tuple translation and vice-versa.
**(stream, message)** tuples are recognised by the classes in :mod:`covertutils.handlers` but data transmission is only possible with `raw data`.


	"""
	__metaclass__ = ABCMeta

	__pass_encryptor = ascii_letters * 10

	def __init__( self, passphrase, tag_length, cycling_algorithm = None, streams = [], history = 1, reverse = False ) :
		self.compressor = Compressor()

		self.cycling_algorithm = cycling_algorithm
		if self.cycling_algorithm == None:
			self.cycling_algorithm = StandardCyclingAlgorithm

		passGenerator = StandardCyclingKey( passphrase, cycling_algorithm = self.cycling_algorithm )
		self.id_value = passGenerator.encrypt( self.__pass_encryptor )
		strIdentifierSeed = passGenerator.encrypt( self.__pass_encryptor )

		self.reverse = reverse
		self.streamIdent = StreamIdentifier( strIdentifierSeed, reverse = reverse, stream_list = streams, cycling_algorithm = self.cycling_algorithm )

		self.default_stream = self.streamIdent.getHardStreamName()
		if self.default_stream not in streams :
			streams.insert( 0, self.default_stream )

		self.streams_buckets = {}
		self.__key_generator = passGenerator.encrypt( self.__pass_encryptor )

		for stream in streams :
			self.addStream( stream )
			# self.__key_generator = passGenerator.encrypt( self.__key_generator )

		self.tag_length = tag_length
		self.history_queue = []
		self.history_length = history
		self.identity = self.generateIdentity( )


	def generateIdentity( self, *args ) :
		identity_str =  ''.join([ str(x) for x in args ]) + self.id_value + str(self.tag_length) + str(set(self.streams_buckets.keys()))
		return  self.cycling_algorithm( identity_str ).hexdigest()


	def getIdentity( self, length = 16 ) :
		"""
:param int length: The length of hex bytes to be returned. Defaults to '16'. If a number greater than the available `identity` string is passed, the whole `identity` hash will be returned.
		"""
		ret = self.identity[:length]
		if self.reverse :
			true_str = 'F' * length
			return xor_str( true_str.decode('hex'), ret.decode('hex') ).encode('hex')
		return ret


	def checkIdentity( self, identity ) :
		"""
:param str identity: The identity hash of the `Orchestrator` object to be checked for compatibility.
:rtype bool:
:return: Returns `True` if the `Orchestrator` with the passed identity is compatible, `False` if it has the same specs but needs the `reverse` argument toggled, and `None` if it is incompatible (initialized with different *password*, *tag_length*, *streams*, etc).

		"""
		length = len(identity)
		my_id = self.getIdentity( length )
		if identity == my_id : return False
		ret = xor_str( my_id.decode('hex'), identity.decode('hex') )
		if ret == '\xFF' * len(ret) :
			return True
		return None


	def deleteStream( self, stream ) :
		self.streamIdent.deleteStream( stream )
		del self.streams_buckets[ stream ]


	def addStream( self, stream ) :

		if stream in self.getStreams() : return False
		if stream not in self.streamIdent.getStreams() :
			self.streamIdent.addStream( stream )

		self.streams_buckets[ stream ] = {}
		self.streams_buckets[ stream ]['message'] = ''
		self.streams_buckets[ stream ]['chunker'] = None
		self.streams_buckets[ stream ]['keys'] = { 'decryption' : None, 'encryption' : None }

		not_hard_stream = self.streamIdent.getHardStreamName() != stream
		encryption_key = StandardCyclingKey( self.__key_generator+stream, cycling_algorithm = self.cycling_algorithm, cycle = not_hard_stream )
		decryption_key = StandardCyclingKey( self.__key_generator[::-1]+stream, cycling_algorithm = self.cycling_algorithm, cycle = not_hard_stream )

		if self.reverse  :
			encryption_key, decryption_key = decryption_key, encryption_key
		self.streams_buckets[stream]['keys']['encryption'] = encryption_key
		self.streams_buckets[stream]['keys']['decryption'] = decryption_key
		return True


	def getChunkerForStream( self, stream ) :
		chunker = self.streams_buckets[ stream ]['chunker']
		return chunker


	def __add_to_history( self, chunk ) :
		while len(self.history_queue) > self.history_length :
			self.history_queue.pop()
		self.history_queue.insert( 0, chunk )


	def getHistoryChunk( self, index = 0 ) :
		return self.history_queue[ index ]


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
		for stream in self.getStreams() :
			for key in self.streams_buckets[stream]['keys'].values() :
				key.reset()
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
		compressed = self.compressor.compress( message )

		chunker = self.getChunkerForStream( stream )
		chunks = chunker.chunkMessage( compressed )
		ready_chunks = []
		for chunk in chunks :
			tag = self.streamIdent.getIdentifierForStream( stream,
				byte_len = self.tag_length )
			encryption_key = self.streams_buckets[stream]['keys']['encryption']
			encr_chunk = encryption_key.encrypt( chunk )

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
		decryption_key = self.streams_buckets[stream]['keys']['decryption']
		decr_chunk = decryption_key.decrypt( chunk )
		status, message = chunker.deChunkMessage( decr_chunk )
		if status :
			message = self.compressor.decompress( message )
			self.streams_buckets[ stream ]['message'] = message
			return stream, message
		return stream, None
