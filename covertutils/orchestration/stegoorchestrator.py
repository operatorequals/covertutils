
from covertutils.crypto.keys import StandardCyclingKey
from covertutils.crypto.algorithms import StandardCyclingAlgorithm

from covertutils.datamanipulation import Chunker
from covertutils.datamanipulation import Compressor

from covertutils.orchestration import StreamIdentifier
from covertutils.orchestration import Orchestrator

from covertutils.datamanipulation import StegoInjector, DataTransformer

from string import ascii_letters

from os import urandom


def _dummy_function( data, encode = False ) :
	return data



class StegoOrchestrator ( Orchestrator ) :
	"""
The `StegoOrchestrator` class combines compression, chunking, encryption and stream tagging, by utilizing the below `covertutils` classes:

 - :class:`covertutils.datamanipulation.Chunker`
 - :class:`covertutils.datamanipulation.Compressor`
 - :class:`covertutils.crypto.keys.StandardCyclingKey`
 - :class:`covertutils.orchestration.StreamIdentifier`

	"""

	__pass_encryptor = ascii_letters * 10

	def __init__( self, passphrase, stego_config, transformation_list = [], tag_length = 2, cycling_algorithm = None, intermediate_function = _dummy_function, reverse = False ) :

		self.intermediate_function = intermediate_function
		self.stego_injector = StegoInjector( stego_config )
		self.data_tranformer = DataTransformer( stego_config, transformation_list )
		self.compressor = Compressor()

		self.cycling_algorithm = cycling_algorithm
		if self.cycling_algorithm == None:
			self.cycling_algorithm = StandardCyclingAlgorithm


		streams = self.stego_injector.getTemplates()

		super( StegoOrchestrator, self ).__init__( passphrase, tag_length, cycling_algorithm, streams, reverse )

		self.__simple_orchestrators = {}
		for index, template in enumerate( streams ) :
			stego_capacity = self.stego_injector.getCapacity( template )
			# print stego_capacity
			inter_product = self.intermediate_function( "0" * stego_capacity, False )	# Need a valid decodable data string "0000..." is valid hex
			intermediate_cap = len( inter_product )	 - self.tag_length # check the capacity of the data length after the intermediate function

			self.streams_buckets[ template ]['chunker'] = Chunker( intermediate_cap, intermediate_cap, reverse = reverse )



	def readyMessage( self, message, stream ) :

		chunks = super( StegoOrchestrator, self ).readyMessage( message, stream )

		ready_chunks = []
		for chunk in chunks :

			# print chunk.encode('hex')
			modified_chunk = self.intermediate_function( chunk, True )

			injected = self.stego_injector.inject( modified_chunk, stream )
			transformed = self.data_tranformer.runAll( injected, stream+"_alt" )

			ready_chunks.append( transformed )

		return ready_chunks



	def depositChunk( self, chunk ) :

		templ = self.stego_injector.guessTemplate( chunk )[0]
		extr_data = self.stego_injector.extract( chunk, templ )
		chunk = self.intermediate_function( extr_data, False )

		ret = super( StegoOrchestrator, self ).depositChunk( chunk )
		return ret
