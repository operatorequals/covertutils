"""
This module provides classes for translating raw data into `(stream, message)` tuples, usable by the :class:`covertutils.handlers.BaseHandler` and subclasses.


"""
from string import ascii_letters
from copy import deepcopy

from covertutils.exceptions import *

from covertutils.crypto.keys import StandardCyclingKey
from covertutils.crypto.algorithms import StandardCyclingAlgorithm

from covertutils.datamanipulation import Chunker
from covertutils.datamanipulation import Compressor


class StreamIdentifier :

	__comparer = ascii_letters

	def __init__( self, passphrase, stream_list = [], cycling_algorithm = None, reverse = False, hard_stream = 'control' ) :

		self.cycle = False		# For testing
		if cycling_algorithm == "No" :
			self.cycle = False

		self.cycling_algorithm = cycling_algorithm
		if self.cycling_algorithm == None :
			self.cycling_algorithm = StandardCyclingAlgorithm

		self.__streams = {}
		self.hashphrase = self.cycling_algorithm( passphrase ).digest()

		stream_list = set( stream_list )
		self.__hard_stream = hard_stream
		stream_list.add( self.__hard_stream )	# be sure that the list contains a control stream
		# self.__stream_generator = StandardCyclingKey( passphrase, cycling_algorithm )

		self.reverse = reverse
		for stream_name in stream_list :
			self.addStream( stream_name )


	def addStream( self, stream_name ) :
		if stream_name in self.__streams.keys() :
			raise StreamAlreadyExistsException( "Stream '%s' already exists" % stream_name )

		inp_passphrase = self.cycling_algorithm( self.hashphrase + stream_name ).digest()
		out_passphrase = self.cycling_algorithm( stream_name + self.hashphrase ).digest()

		if self.reverse :
			inp_passphrase, out_passphrase = out_passphrase, inp_passphrase

		inp_StandardCyclingKey = StandardCyclingKey ( inp_passphrase, cycling_algorithm = self.cycling_algorithm  )
		out_StandardCyclingKey = StandardCyclingKey ( out_passphrase, cycling_algorithm = self.cycling_algorithm )

		StandardCyclingKey_tuple = ( inp_StandardCyclingKey, out_StandardCyclingKey )
		self.__streams[stream_name] = StandardCyclingKey_tuple


	def deleteStream( self, stream_name ) :
		if stream_name == self.__hard_stream :
			raise StreamDeletionException( "Control Stream cannot be deleted!" )
		del self.__streams[ stream_name ]


	def getHardStreamName( self ) :
		return self.__hard_stream


	def getIdentifierForStream( self, stream_name = None, byte_len = 2 ) :
		if stream_name == None :
			stream_name = self.__hard_stream

		assert stream_name in self.__streams.keys()

		StandardCyclingKeys = self.__streams[ stream_name ]
		out_StandardCyclingKey = self.__streams[ stream_name ][1]

		ident = out_StandardCyclingKey.xor( self.__comparer[:byte_len] )

		hardIdentify = (stream_name == self.__hard_stream)
		self.__cycleKey( out_StandardCyclingKey, hardIdentify )

		return ident


	def checkIdentifier( self, bytes_ ) :
		byte_len = len( bytes_ )

		for stream_name, StandardCyclingKeys in self.__streams.items() :
			inp_StandardCyclingKey = StandardCyclingKeys[0]
			hardIdentify = (stream_name == self.__hard_stream)

			plain = inp_StandardCyclingKey.xor( bytes_ )
			if plain == self.__comparer[:byte_len] :
				self.__cycleKey( inp_StandardCyclingKey, hardIdentify )
				return stream_name
		return None


	def __cycleKey( self, key, hardIdentify ) :
		if not self.cycle : return
		if not hardIdentify :
			key.cycle()


	def getStreams( self, ) :
		return self.__streams.keys()


	def reset( self ) :
		for stream_name, StandardCyclingKeys in self.__streams.items() :
			for key in StandardCyclingKeys :
				key.reset()



class Orchestrator :

	__metaclass__ = ABCMeta




class SimpleOrchestrator :
	"""
The `SimpleOrchestrator` class combines compression, chunking, encryption and stream tagging, by utilizing the below `coverutils` classes:

 - :class:`covertutils.datamanipulation.Chunker`
 - :class:`covertutils.datamanipulation.Compressor`
 - :class:`covertutils.crypto.keys.StandardCyclingKey`
 - :class:`covertutils.orchestration.StreamIdentifier`

	"""

	__pass_encryptor = ascii_letters * 10

	def __init__( self, passphrase, tag_length = 2, out_length = 10, in_length = 10, streams = ['main'], cycling_algorithm = None, reverse = False ) :
		"""
:param str passphrase: The `passphrase` is the seed used to generate all encryption keys and stream identifiers. Two `SimpleOrchestrator` objects are compatible (can understand each other products) if they are initialized with the same `passphrase`. As `passphrase` is data argument, it is Case-Sensitive, and arbitrary bytes (not just printable strings) can be used.
:param int tag_length: Every `Stream` is identified by a Tag, that is also data, appended to every `Message` chunk. The byte length of those tags can be set by this argument. Too small tags can mislead the `Orchestrator` object to recognise arbitrary data and try to process it (start decompressing it, decrypt it). Too large tags spend too much of a chunks bandwidth.
:param int out_length: The data length of the chunks that are returned by the :func:`coverutils.orchestration.SimpleOrchestrator.readyMessage`.
:param int in_length: The data length of the chunks that will be passed to :func:`coverutils.orchestration.SimpleOrchestrator.depositChunk`.
:param list streams: The list of all streams needed to be recognised by the `SimpleOrchestrator`. A "control" stream is always hardcoded in a `SimpleOrchestrator` object.
:param class cycling_algorithm: The hashing/cycling function used in all crypto and stream identification. If not specified the :class:`covertutils.crypto.algorithms.StandardCyclingAlgorithm` will be used. The :class:`hashlib.sha256` is a great choice if `hashlib` is available.
:param bool reverse: If this is set to `True` the `out_length` and `in_length` are internally reversed in the instance. This parameter is typically used to keep the parameter list the same between 2 `SimpleOrchestrator` initializations, yet make them `compatible`.
		"""

		self.out_length = out_length - tag_length
		self.in_length = in_length - tag_length
		self.compressor = Compressor()

		self.cycling_algorithm = cycling_algorithm
		if self.cycling_algorithm == None:
			self.cycling_algorithm = StandardCyclingAlgorithm

		passGenerator = StandardCyclingKey( passphrase, cycling_algorithm = self.cycling_algorithm )
		pass1 = passGenerator.xor( self.__pass_encryptor )
		pass2 = passGenerator.xor( self.__pass_encryptor )

		self.streamIdent = StreamIdentifier( pass1, reverse = reverse, cycling_algorithm = self.cycling_algorithm )

		self.default_stream = self.streamIdent.getHardStreamName()
		streams.append( self.default_stream )

		self.encryption_key = StandardCyclingKey( pass2, cycling_algorithm = self.cycling_algorithm )
		self.decryption_key = StandardCyclingKey( pass2, cycling_algorithm = self.cycling_algorithm )

		self.reverse = reverse
		self.streams_buckets = {}
		for stream in streams :
			self.addStream( stream )

		self.tag_length = tag_length

		del passGenerator
		del passphrase


	def getDefaultStream( self ) :
		"""
This method returns the stream that is used if no stream is specified in `readyMessage()`.

:rtype: str
		"""
		return self.default_stream


	def addStream( self, stream ) :

		if stream != self.streamIdent.getHardStreamName() :
			self.streamIdent.addStream( stream )

		self.streams_buckets[ stream ] = {}
		self.streams_buckets[ stream ]['message'] = ''
		self.streams_buckets[ stream ]['chunker'] = Chunker( self.out_length,
															self.in_length,
															reverse = self.reverse )


	def deleteStream( self, stream ) :
		self.streamIdent.deleteStream( stream )
		del self.streams_buckets[ stream ]


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


	def __dissectTag( self, chunk ) :
		return chunk[-self.tag_length:], chunk[:-self.tag_length]


	def __addTag( self, chunk, tag ) :
		return chunk + tag


	def reset( self ) :
		"""
This method resets all components of the `SimpleOrchestrator` instance, effectively flushing the Chunkers, restarting One-Time-Pad keys, etc.
		"""
		for stream in self.streams_buckets.keys() :
			self.streams_buckets[ stream ]['message'] = ''
			chunker = self.getChunkerForStream( stream )
			chunker.reset()
		self.encryption_key.reset()
		self.decryption_key.reset()
		self.streamIdent.reset()


#
#
#
#
# class StegoOrchestrator :
# 	"""
# The `StegoOrchestrator` class combines compression, chunking, encryption and stream tagging, by utilizing the below `coverutils` classes:
#
#  - :class:`covertutils.datamanipulation.Chunker`
#  - :class:`covertutils.datamanipulation.Compressor`
#  - :class:`covertutils.crypto.keys.StandardCyclingKey`
#  - :class:`covertutils.orchestration.StreamIdentifier`
#
# 	"""
#
# 	__pass_encryptor = ascii_letters * 10
#
# 	def __init__( self, passphrase, stego_config, transformation_list, cycling_algorithm = None, reverse = False ) :
#
# 		self.stego_injector = StegoInjector( stego_config )
# 		self.data_tranformer = DataTransformer( stego_config, transformation_list )
#
# 		templates = self.stego_injector.getTemplates()
# 		self.streamIdent = StreamIdentifier( passphrase, reverse = reverse, cycling_algorithm = self.cycling_algorithm, streams = templates )
#
#
#
#
# 	def readyMessage( self, stream, message ) :
# 		pass
