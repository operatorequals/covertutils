from abc import ABCMeta, abstractmethod
# from time import sleep
from covertutils.handlers import BaseHandler
from covertutils.helpers import defaultArgMerging



class BufferingHandler( BaseHandler ) :
	"""
Subclassing this class and overriding its methods automatically creates a threaded handler.
"""
	__metaclass__ = ABCMeta

	def __init__( self,  recv, send, orchestrator, **kw ) :

		super( BufferingHandler, self ).__init__( recv, send, orchestrator, **kw )
		self.__buffer = []


	def onMessage( self, stream, message ) :
		self.buffer.append( (stream, message) )


	def pop( self ) :
		return self.__buffer.pop(0)


	def count( self ) :
		return len( self.__buffer )
