from abc import ABCMeta, abstractmethod

from binascii import hexlify



class CyclingAlgorithm :

	__metaclass__ = ABCMeta

	def __init__( self, message ) :
		self.message = message


	def update( self, message ) :
		self.message += message


	@abstractmethod
	def digest( self ) :
		pass


	def hexdigest( self ) :
		bin_ = self.digest()
		return hexlify( bin_ )
