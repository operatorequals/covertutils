from covertutils.crypto.keys import StandardCyclingKey
from covertutils.crypto.algorithms import StandardCyclingAlgorithm

from covertutils.datamanipulation import AdHocChunker
from covertutils.datamanipulation import Chunker

from covertutils.orchestration import StreamIdentifier
from covertutils.orchestration import Orchestrator

from covertutils.datamanipulation import StegoInjector, DataTransformer

from string import ascii_letters

from os import urandom

from covertutils.helpers import copydoc

def _dummy_function( data, encode = False ) :
	return data



class StegoOrchestrator ( Orchestrator ) :
	"""
The `StegoOrchestrator` class combines compression, chunking, encryption, stream tagging and steganography injection, by utilizing the below `covertutils` classes:

 - :class:`covertutils.datamanipulation.AdHocChunker`
 - :class:`covertutils.datamanipulation.Compressor`
 - :class:`covertutils.crypto.keys.StandardCyclingKey`
 - :class:`covertutils.orchestration.StreamIdentifier`
 - :class:`covertutils.datamanipulation.StegoInjector`
 - :class:`covertutils.datamanipulation.DataTransformer`


The `StegoOrchestrator` packs `(stream, message)` pairs in predefined data templates.
	"""

	def __init__( self, passphrase, stego_config, main_template, transformation_list = [], tag_length = 2, cycling_algorithm = None, streams = [], hex_inject = False, reverse = False ) :
		"""
:param str stego_config: The configuration that is passed to :class:`covertutils.datamanipulation.stegoinjector.StegoInjector`.
:param str main_template: The default template that will be used in :func:`readyMessage()` `template` argument.
:param list transformation_list: The Transformation List that is passed to the :class:`covertutils.datamanipulation.datatransformer.DataTransformer` object.
:param class cycling_algorithm: The hashing/cycling function used in all OTP crypto and stream identification. If not specified the  :class:`covertutils.crypto.algorithms.StandardCyclingAlgorithm` will be used. The :class:`hashlib.sha256` is a great choice if `hashlib` is available.
:param list streams: The list of all streams needed to be recognised by the `SimpleOrchestrator`. A "control" stream is always hardcoded in a `SimpleOrchestrator` object.
:param func intermediate_function: A *codec* function with signature `codec( data, encode = False )`. The function is called before and injection of a chunk with *encode = True* and after the extraction of a chunk with *encode = False*.
:param bool reverse: If this is set to `True` a `StegoOrchestrator` with reverse streams is created. This parameter is typically used to keep the parameter list the same between 2 `StegoOrchestrator` initializations, yet make them `compatible`.
		"""

		self.stego_injector = StegoInjector( stego_config, hex_inject )
		self.data_tranformer = DataTransformer( stego_config, transformation_list )

		self.cycling_algorithm = cycling_algorithm
		if self.cycling_algorithm == None:
			self.cycling_algorithm = StandardCyclingAlgorithm

		self.main_template = main_template
		self.current_template = main_template

		self.chunk_sizes = {}

		super( StegoOrchestrator, self ).__init__( passphrase, tag_length = tag_length, cycling_algorithm = cycling_algorithm, streams = streams, history = 1, reverse = reverse )

		for index, template in enumerate( self.stego_injector.getTemplates() ) :
			stego_capacity = self.stego_injector.getCapacity( template )
		# 	# print stego_capacity
		# 	# inter_product = self.intermediate_function( "0" * stego_capacity, False )	# Need a valid decodable data string "0000..." is valid hex, base64, etc
			# intermediate_cap = stego_capacity - self.tag_length 		# check the capacity of the data length after the intermediate function
		#
			intermediate_cap = stego_capacity 		# check the capacity of the data length after the intermediate function
		# 	# intermediate_cap = len( inter_product )	 		# check the capacity of the data length after the intermediate function
		#
			self.chunk_sizes[template] = intermediate_cap


	@copydoc(Orchestrator.readyMessage)
	def readyMessage( self, message, stream = None ) :

		template = self.current_template
		if stream == None :
			stream = self.default_stream

		# template_capacity = self.stego_injector.getCapacity( template )
		template_capacity = self.chunk_sizes[template]
		# print "Lengths: template_length = %d" % template_capacity
		self.streams_buckets[ stream ]['chunker'].setChunkSize( template_capacity )
		chunks = super( StegoOrchestrator, self ).readyMessage( message, stream )
		# print "Lengths: chunk_length = %d" % len(chunks[0])

		ready_chunks = []
		for chunk in chunks :

			modified_chunk = chunk
			# modified_chunk = self.intermediate_function( chunk, True )
			# print "<--"
			# print chunk.encode('hex')
			# print modified_chunk.encode('hex')
			injected = self.stego_injector.inject( modified_chunk, template )

			alterations = self.__getAlterations( template )			# needs to be documented

			transformed = injected
			for alteration_templ in alterations :
				transformed = self.data_tranformer.runAll( transformed, alteration_templ )

			ready_chunks.append( transformed )
		return ready_chunks


	@copydoc(Orchestrator.depositChunk)
	def depositChunk( self, chunk ) :
		templ = self.stego_injector.guessTemplate( chunk )
		if templ == None :
			return (None, None)			# Trigger the notRecognised() method of the underlying Handler
		self.received_template = templ[0]
		extr_data = self.stego_injector.extract( chunk, self.received_template )

		ret = super( StegoOrchestrator, self ).depositChunk( extr_data )
		return ret


	@copydoc(Orchestrator.addStream)
	def addStream( self, stream ) :
		super( StegoOrchestrator, self ).addStream( stream )
		self.streams_buckets[ stream ]['chunker'] = AdHocChunker()


	def useTemplate( self, template ) :
		"""
:param str template: The template to use for the next Message. Use `None` for random templates.
		"""
		self.current_template = template


	def lastReceivedTemplate( self ) :
		"""
:rtype: str
:return: Returns the last template received.
		"""
		return self.received_template


	def __getAlterations( self, template ) :		# Document the '_alt' suffix
		templates = self.stego_injector.getTemplates()
		ret = []
		for templ in templates :
			if templ.startswith( template+"_alt" ) :
				ret.append( templ )
		return ret
