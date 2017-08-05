from abc import ABCMeta, abstractmethod

from covertutils.datamanipulation import Chunker
from covertutils.datamanipulation import Compressor

from covertutils.crypto.keys import StandardCyclingKey
from covertutils.crypto.algorithms import StandardCyclingAlgorithm

#
# class Orchestrator :
#
# 	__metaclass__ = ABCMeta
#
# 	def __init__( passphrase, cycling_algorithm = None, streams = [], reverse = False ) :
		# self.compressor = Compressor()
		#
		# self.cycling_algorithm = cycling_algorithm
		# if self.cycling_algorithm == None:
		# 	self.cycling_algorithm = StandardCyclingAlgorithm
		#
		# passGenerator = StandardCyclingKey( passphrase, cycling_algorithm = self.cycling_algorithm )
		# pass1 = passGenerator.xor( self.__pass_encryptor )
		# pass2 = passGenerator.xor( self.__pass_encryptor )
		#
		# self.encryption_key = StandardCyclingKey( pass2, cycling_algorithm = self.cycling_algorithm )
		# self.decryption_key = StandardCyclingKey( pass2, cycling_algorithm = self.cycling_algorithm )
		#
		# self.reverse = reverse
		#
		# self.streamIdent = StreamIdentifier( pass1, reverse = reverse, cycling_algorithm = self.cycling_algorithm )
		#
		# self.default_stream = self.streamIdent.getHardStreamName()
		# streams.append( self.default_stream )
		#
		# self.streams_buckets = {}
		# for stream in streams :
		# 	self.addStream( stream )
		#
		# self.tag_length = tag_length
		#

#
# 	@abstractmethod
# 	def
