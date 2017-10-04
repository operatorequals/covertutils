from covertutils.handlers import BufferingHandler
from covertutils.orchestration import Orchestrator
from covertutils.bridges import SimpleBridge

from time import sleep
from functools import wraps

try :
	from queue import Queue
except ImportError:
	from Queue import Queue

def handlerCallbackHook( instance, on_chunk_function, orch_id ) :

	# print( "In the Hook" )
	@wraps(on_chunk_function)
	def wrapper( *args, **kwargs ) :
		# print( "In the Wrapper" )
		stream, message = args
		pseudo_stream = "%s:%s" % (orch_id, stream)
		if message :
			# print( stream, message )
			# print args
			instance.onMessage( pseudo_stream, message )
		else :
			instance.onChunk( pseudo_stream, message )

		on_chunk_function( *args, **kwargs )		# Not honoring return values
		return on_chunk_function
	return wrapper


class MultiHandler( BufferingHandler ) :
	"""
A class that aggregates multiple :class:`BaseHandler` parented objects, to support parallel session handling.

It supports the standard :meth:`onMessage` API of the original :class:`BaseHandler` objects, as well as methods for dispatching `messages` en-masse.

	"""
	class __NullOrchestrator(Orchestrator) :

		def readyMessage( self, message, stream ) :
			# print "ready"
			assert False == True		# This is dummy, dead code
			return "%s:%s" % (stream, message)

		def depositChunk( self, chunk ) :
			# print "deposit"
			assert False == True		# This is dummy, dead code
			stream, message = chunk.split(':',1)
			return stream, message



	def start(self) : pass
	def nullSend( self, message, stream ) : print "nullSend" ; pass
	# def onChunk( self, stream, message ) : pass
	# def onNotRecognised( self ) : pass

	def __init__( self, handlers, **kw ) :
		assert type(handlers == list)

		def send_internal(raw) :
			print "++++++++Send internal run+++++"
			assert False == True		# This is dummy, dead code

		def recv_internal() :
			print "=========recv internal run======="
			assert False == True		# This is dummy, dead code
			return None

		orch = MultiHandler.__NullOrchestrator("", 0)
		super(MultiHandler, self).__init__(recv_internal, send_internal, orch, **kw)
		# self.preferred_send = self.nullSend

		self.handlers = {}
		for handler in handlers :
			self.addHandler(handler)


	def resolveStream( self, stream_alias ) :
		orch_id, stream = stream_alias.split(':',1)
		handler = self.handlers[orch_id]['handler']
		return handler, stream


	def preferred_send( self, message, stream ) :
		handler, stream = self.resolveStream( stream )
		handler.preferred_send( message, stream )
		print "RUNI"

	def queueSend( self, message, stream ) :
		pass


	def dispatch( self, orch_ids, stream, message ) :
		for orch_id in orch_ids :
			handler = self.handlers[orch_id]['handler']
			handler.preferred_send( message, stream )

	def dispatchTo( self, orch_id, stream, message ) :
		self.dispatch( [orch_id], stream, message )

	def dispatchAll( self, message, stream = 'control' ) :	# Make it look for hard_streams when stream = None
		for orch_id in self.handlers.keys() :
			if stream in self.handlers[orch_id]['streams'] :
				handler = self.handlers[orch_id]['handler']
				handler.preferred_send( message, stream )
	#
	# def sendTo( self, orch_id, message, stream = 'control', local = True ) :	# Make it look for hard_streams when stream = None
	# 	for orch_id_ in self.handlers.keys() :
	# 		handler = self.handlers[orch_id]['handler']
	# 		if local :
	# 			orch = handler.getOrchestrator()
	# 			orch_to_check = orch.getIdentity()
	# 		else :
	# 		for x,y in zip(orch_id, orch_id_) :
	# 			if z
	# 		# if orch.checkIdentity(orch_id) ==
	#
	# 		if stream in self.handlers[orch_id]['streams'] :
	# 			handler = self.handlers[orch_id]['handler']
	# 			handler.preferred_send( message, stream )

	def getHandler(self, orch_id) :
		return self.handlers[orch_id]['handler']

	def getAllHandlers(self) :
		return [self.handlers[o_id]['handler'] for o_id in self.handlers.keys()]


	def addStream( self, stream ) :
		for orch_id in self.getOrchestratorIDs() :
			self.__add_stream(orch_id, stream)


	def __add_stream(self, orch_id, stream) :
		self.handlers[orch_id]['streams'].append(stream)

		pseudo_stream = "%s:%s" % (orch_id, stream)	# not used
		self.getOrchestrator().addStream(pseudo_stream)


	def addHandler(self, handler) :
		orch_id = handler.getOrchestrator().getIdentity()
		self.handlers[orch_id] = {}
		self.handlers[orch_id]['streams'] = []

		buffered_handler = BufferingHandler.bufferize_handler_obj(handler)
		# self.handlers[orch_id]['bridge'] = SimpleBridge( self, buffered_handler )
		self.handlers[orch_id]['handler'] = buffered_handler

		buffered_handler.onChunk = handlerCallbackHook( self, buffered_handler.onChunk, orch_id )

		for stream in handler.getOrchestrator().getStreams() :
			# print pseudo_stream
			self.__add_stream(orch_id, stream)


	def getOrchestratorIDs(self) :
		return self.handlers.keys()
