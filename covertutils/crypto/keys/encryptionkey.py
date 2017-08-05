from abc import ABCMeta, abstractmethod


class EncryptionKey :

	__metaclass__ = ABCMeta

	@abstractmethod
	def encrypt( self, plain ) : pass
	@abstractmethod
	def decrypt( self, crypt ) : pass
