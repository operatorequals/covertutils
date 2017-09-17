from abc import ABCMeta, abstractmethod
# from time import sleep
from covertutils.handlers import BaseHandler
from covertutils.helpers import defaultArgMerging

from threading import Condition, Thread
from multiprocessing import Queue


class BufferingHandler( BaseHandler ) :
	"""
Subclassing this class ensures that all Messages received will be available through a blocking `get()` method, the same way a :class:`queue.Queue` object provides access to its contents.
"""
	__metaclass__ = ABCMeta

	def __init__( self,  recv, send, orchestrator, **kw ) :

		super( BufferingHandler, self ).__init__( recv, send, orchestrator, **kw )
		self.__buffer = Queue()
		self.__condition = Condition()

	def onMessage( self, stream, message ) :
		# print "Before acquire()"
		self.__condition.acquire()
		# print "Before Put"
		self.__buffer.put( (stream, message) )
		# print "Before notify()"
		self.__condition.notify()
		# print "Before release()"
		self.__condition.release()
		# print "released"
		# print "Before super()"
		# super(BufferingHandler, self).onMessage( stream, message )


	def get( self ) :
		'''
Blocking call that wraps the internal buffer's `get()` function
		'''
		return self.__buffer.get()


	def empty( self ) :
		return self.__buffer.empty()


	def getCondition( self ) :
		return self.__condition


 	@staticmethod
 	def bufferize_handler( handler_class ) :
		'''
Pairs a class with `BufferingHandler` class to create a child class, inheriting from both the passed `handler_class` and `BufferingHandler` class.
		'''
 		class BufferizedHandler(BufferingHandler, handler_class) :
 			def __init__(self, recv, send, orch, **kw) :
 				super(BufferizedHandler, self).__init__(recv, send, orch, **kw)
 		return BufferizedHandler


 	@staticmethod
 	def bufferize_handler_obj( handler_obj ) :
		'''
Migrate an existing object inheriting from `BaseHandler` to be an effective child of `BufferingHandler`.

Attaches the `BufferingHandler` as a parent class in `__class__` object field and runs the specialized `__init__` for `BufferingHandler` inside the objects context.
`BufferingHandler.__init__` has to run in the object in order to initiate the buffering process of `BufferingHandler`.
		'''
		if isinstance(handler_obj, BufferingHandler) : return handler_obj
		handler_class = handler_obj.__class__
 		bufferized_class = BufferingHandler.bufferize_handler( handler_class )
		handler_obj.__class__ = bufferized_class

		# super(handler_obj.__class__, handler_obj).__init__(handler_obj.receive_function, handler_obj.send_function, handler_obj.getOrchestrator())
		# super(BufferingHandler, handler_obj).__init__(handler_obj.receive_function, handler_obj.send_function, handler_obj.getOrchestrator())
		BufferingHandler.__init__(handler_obj, handler_obj.receive_function, handler_obj.send_function, handler_obj.getOrchestrator())	# Runs the __init__ code only for BufferingHandler

 		return handler_obj
