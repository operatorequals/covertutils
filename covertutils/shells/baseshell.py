from abc import ABCMeta

from covertutils.handlers import BaseHandler
from covertutils.helpers import defaultArgMerging
import covertutils

from functools import wraps

from threading import Condition, Thread
from multiprocessing import Queue

import sys
import cmd


def handlerCallbackHook( handler_function, store_queue, store_condition ) :

	# print "In the Hook"
	@wraps(handler_function)
	def wrapper( *args, **kwargs ) :
		# print "In the Wrapper"
		store_condition.acquire()
		store_queue.put( args )
		store_condition.notify()
		store_condition.release()

		handler_function( *args, **kwargs )		# Not honoring return values
		return handler_function
	return wrapper



class BaseShell( cmd.Cmd ) :

	# __metaclass__ = ABCMeta

	stream_preamp_char = "!"
	control_preamp_char = ":"
	ruler = "><"
	Defaults = { 'prompt' : "(%s v%s)[{0}]> " % ( covertutils.__name__, covertutils.__version__ ) }

	def __init__( self, handler,
		message_function_dict = None,
		log_messages = True, log_chunks = False, log_unrecognised = False, **kw ) :

		cmd.Cmd.__init__(self)

		arguments = defaultArgMerging(self.Defaults, kw)
		self.prompt_templ = arguments['prompt']

		self.orchestrator = handler.getOrchestrator()
		self.current_stream = self.orchestrator.getDefaultStream()
		self.updatePrompt()

		self.handler = handler
		self.message_list = Queue()
		self.chunk_list = Queue()
		self.not_recognised_list = Queue()

		if log_messages :
			queue, condition = self.start_response_worker( "message" )
			handler.onMessage = handlerCallbackHook( handler.onMessage, queue, condition )

		if log_chunks :
			queue, condition = self.start_response_worker( "chunks" )			# A lingering bug on queue and condition names
			handler.onChunk = handlerCallbackHook( handler.onChunk, queue, condition )

		if log_unrecognised :
			queue, condition = self.start_response_worker( "notRecognised" )			# A lingering bug on queue and condition names
			handler.onNotRecognised = handlerCallbackHook( handler.onNotRecognised, queue, condition )

		self.message_function_dict = message_function_dict


	def start_response_worker( self, name ) :
		condition = Condition()
		queue = Queue()
		messageCallbackThread = Thread( target = self.__response_worker, args = (queue, condition) )
		messageCallbackThread.name = name
		messageCallbackThread.daemon = True
		messageCallbackThread.start()
		return queue, condition


	def __response_worker( self, queue, condition ) :
		while True :
			condition.acquire()
			if queue.empty() :
				condition.wait()
			stream, message = queue.get()
			self.message_function_dict[stream]( message )
			condition.release()


	def updatePrompt( self ) :
		self.prompt = self.prompt_templ.format( self.current_stream )


	def availableStreams(self) :
		return self.orchestrator.getStreams()


	def default( self, line ) :
		if not line.startswith( self.stream_preamp_char ) :
			self.handler.preferred_send( line, self.current_stream )
			return
		line = line[1:]
		if line in self.availableStreams() :
			self.current_stream = line
		else :
			print ( "Available streams:\n	[+] " + '	\n	[+] '.join(self.availableStreams()) )
		self.updatePrompt()
		return


	def emptyline( self ) :
		return


	def do_EOF( self, line ) :
		print
		return


	def start( self ) :

		while True :
			try :
				self.cmdloop()
			except KeyboardInterrupt :
				# sys.exit(0)			# Test purposes ONLY!
				print
				exit_input = raw_input("Really Control-C [y/N]? ")
				if exit_input == 'y' :
					print "Aborted by the user..."
					sys.exit(0)
