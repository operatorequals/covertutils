from abc import ABCMeta, abstractmethod
# from time import sleep
from covertutils.handlers import BaseHandler
from covertutils.helpers import defaultArgMerging

from threading import Condition, Thread
from queue import Queue


class BufferingHandler( BaseHandler ) :
	"""
Subclassing this class and overriding its methods automatically creates a threaded handler.
"""
	__metaclass__ = ABCMeta

	def __init__( self,  recv, send, orchestrator, **kw ) :

		super( BufferingHandler, self ).__init__( recv, send, orchestrator, **kw )
		self.__buffer = Queue()
		self.__condition = Condition()


	def onMessage( self, stream, message ) :
		self.__condition.acquire()
		self.buffer.append( (stream, message) )
		self.__condition.notify()
		self.__condition.release()


	def pop( self ) :
		return self.__buffer.pop(0)


	def count( self ) :
		return len( self.__buffer )


	def getCondition( self ) :
		return self.__condition
