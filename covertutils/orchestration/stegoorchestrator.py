
from covertutils.crypto.keys import StandardCyclingKey
from covertutils.crypto.algorithms import StandardCyclingAlgorithm

from covertutils.datamanipulation import Chunker
from covertutils.datamanipulation import Compressor

from covertutils.datamanipulation import StegoInjector, DataTransformer

from string import ascii_letters


class StegoOrchestrator :
	"""
The `StegoOrchestrator` class combines compression, chunking, encryption and stream tagging, by utilizing the below `coverutils` classes:

 - :class:`covertutils.datamanipulation.Chunker`
 - :class:`covertutils.datamanipulation.Compressor`
 - :class:`covertutils.crypto.keys.StandardCyclingKey`
 - :class:`covertutils.orchestration.StreamIdentifier`

	"""

	__pass_encryptor = ascii_letters * 10

	def __init__( self, passphrase, stego_config, transformation_list = [], tag_length = 2, cycling_algorithm = None, reverse = False ) :

		self.stego_injector = StegoInjector( stego_config )
		self.data_tranformer = DataTransformer( stego_config, transformation_list )
		self.compressor = Compressor()

		self.cycling_algorithm = cycling_algorithm
		if self.cycling_algorithm == None:
			self.cycling_algorithm = StandardCyclingAlgorithm


		templates = self.stego_injector.getTemplates()

		self.streamIdent = StreamIdentifier( passphrase, stream_list = templates, reverse = reverse, cycling_algorithm = self.cycling_algorithm )

		self.tag_length = tag_length

		self.__simple_orchestrators = {}
		for index, template in enumerate( templates ) :
			capacity = self.stego_injector.getCapacity( template ) - self.tag_length
			new_pass = passphrase + str( index )
			self.__simple_orchestrators[ template ] = SimpleOrchestrator( new_pass, 1, capacity, capacity, streams = [template], reverse = reverse, cycling_algorithm = cycling_algorithm)


	def readyMessage( self, message, stream ) :

		message = self.compressor.compress( message )
		orch_obj = self.__simple_orchestrators[ stream ]
		chunks = orch_obj.readyMessage( message, stream )

		ready_chunks = []
		for chunk in chunks :
			tag = self.streamIdent.getIdentifierForStream( stream,
														byte_len = self.tag_length )

			# ready = self.__addTag(encr_chunk, tag)

			ready = chunk
			transformed = self.data_tranformer.runAll( ready, stream )
			injected = self.stego_injector.inject( message, stream, pkt = transformed )

			ready_chunks.append( injected )

		return ready_chunks
