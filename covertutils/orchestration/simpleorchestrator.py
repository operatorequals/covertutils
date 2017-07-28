
from covertutils.crypto.keys import StandardCyclingKey
from covertutils.crypto.algorithms import StandardCyclingAlgorithm

from covertutils.orchestration import StreamIdentifier

from covertutils.orchestration import Orchestrator

from covertutils.datamanipulation import Chunker
from covertutils.datamanipulation import Compressor

from covertutils.helpers import copydoc

from string import ascii_letters

from copy import deepcopy

#
class SimpleOrchestrator ( Orchestrator ) :
	"""
The `SimpleOrchestrator` class combines compression, chunking, encryption and stream tagging, by utilizing the below `covertutils` classes:

 - :class:`covertutils.datamanipulation.Chunker`
 - :class:`covertutils.datamanipulation.Compressor`
 - :class:`covertutils.crypto.keys.StandardCyclingKey`
 - :class:`covertutils.orchestration.StreamIdentifier`

	"""

	def __init__( self, passphrase, tag_length = 2, out_length = 10, in_length = 10, streams = [], cycling_algorithm = None, reverse = False ) :
		"""
:param str passphrase: The `passphrase` is the seed used to generate all encryption keys and stream identifiers. Two `SimpleOrchestrator` objects are compatible (can understand each other products) if they are initialized with the same `passphrase`. As `passphrase` is data argument, it is Case-Sensitive, and arbitrary bytes (not just printable strings) can be used.
:param int tag_length: Every `Stream` is identified by a Tag, that is also data, appended to every `Message` chunk. The byte length of those tags can be set by this argument. Too small tags can mislead the `Orchestrator` object to recognise arbitrary data and try to process it (start decompressing it, decrypt it). Too large tags spend too much of a chunks bandwidth.
:param int out_length: The data length of the chunks that are returned by the :func:`covertutils.orchestration.SimpleOrchestrator.readyMessage`.
:param int in_length: The data length of the chunks that will be passed to :func:`covertutils.orchestration.SimpleOrchestrator.depositChunk`.
:param list streams: The list of all streams needed to be recognised by the `SimpleOrchestrator`. A "control" stream is always hardcoded in a `SimpleOrchestrator` object.
:param class cycling_algorithm: The hashing/cycling function used in all OTP crypto and stream identification. If not specified the  :class:`covertutils.crypto.algorithms.StandardCyclingAlgorithm` will be used. The :class:`hashlib.sha256` is a great choice if `hashlib` is available.
:param bool reverse: If this is set to `True` the `out_length` and `in_length` are internally reversed in the instance. This parameter is typically used to keep the parameter list the same between 2 `SimpleOrchestrator` initializations, yet make them `compatible`.
		"""
		self.out_length = out_length - tag_length
		self.in_length = in_length - tag_length

		super( SimpleOrchestrator, self ).__init__( passphrase, tag_length, cycling_algorithm = cycling_algorithm, streams = streams, reverse = reverse )


		del passphrase

	@copydoc(Orchestrator.addStream)
	def addStream( self, stream ) :
		super(SimpleOrchestrator, self).addStream( stream )
		self.streams_buckets[ stream ]['chunker'] = Chunker( self.out_length,
															self.in_length,
															reverse = self.reverse )


	def reset( self ) :
		"""
This method resets all components of the `SimpleOrchestrator` instance, effectively flushing the Chunkers, restarting One-Time-Pad keys, etc.
		"""
		for stream in self.streams_buckets.keys() :
			self.streams_buckets[ stream ]['message'] = ''
			chunker = self.getChunkerForStream( stream )
			chunker.reset()

		super(SimpleOrchestrator, self).reset()
