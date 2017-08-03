from abc import ABCMeta

# from covertutils.handlers import ResponseOnlyHandler
from covertutils.helpers import defaultArgMerging
import covertutils

from functools import wraps

from threading import Condition, Thread
from Queue import Queue

import sys
import cmd


def handlerCallbackHook( on_chunk_function, stream_dict ) :

	# print "In the Hook"
	@wraps(on_chunk_function)
	def wrapper( *args, **kwargs ) :
		# print "In the Wrapper"
		stream, message = args
		# print stream, message
		if stream not in stream_dict.keys()	:	# No subshell defined for the stream
			return on_chunk_function

		if message :
			stream_dict[stream]['queues']['condition'].acquire()
			stream_dict[stream]['queues']['messages'].put( message )
			stream_dict[stream]['queues']['condition'].notify()
			stream_dict[stream]['queues']['condition'].release()
			stream_dict[stream]['queues']['chunks'] = 0
		else :
			stream_dict[stream]['queues']['chunks'] += 1

		on_chunk_function( *args, **kwargs )		# Not honoring return values
		return on_chunk_function
	return wrapper


class BaseShell( cmd.Cmd ) :
	"""
The base class of the package. It implements basics, like hooking the :class:`covertutils.handlers.basehandler.BaseHandler` and giving a handle for further incoming message proccessing.
	"""

	stream_preamp_char = "!"
	control_preamp_char = ":"
	ruler = "><"
	Defaults = {
		'prompt' : "({package} v{version})> " ,
		# 'ignore_messages' : set([ResponseOnlyHandler.Defaults['request_data']])
		'ignore_messages' : set()
		}

	def __init__( self, handler, log_unrecognised = False, **kw ) :

		cmd.Cmd.__init__(self)
		arguments = defaultArgMerging(BaseShell.Defaults, kw)
		self.prompt_templ = arguments['prompt']
		self.ignore_messages = arguments['ignore_messages']
		subshells = arguments['subshells']

		self.subshells_dict = {}
		self.handler = handler
		for stream_name, subshell_attrs in subshells.items() :
			# if
			if type(subshell_attrs) is tuple :
				subshell_class, subshell_kwargs = subshell_attrs
			else :
				subshell_class, subshell_kwargs = (subshell_attrs, dict())

			self.addSubShell( stream_name, subshell_class, subshell_kwargs )
		handler.onChunk = handlerCallbackHook( handler.onChunk, self.subshells_dict )
		self.updatePrompt()


	def addSubShell( self, stream, subshell_class, subshell_kwargs ) :
		self.subshells_dict[stream] = {}
		self.subshells_dict[stream]['queues'] = {}
		self.subshells_dict[stream]['queues']['messages'] = Queue()
		self.subshells_dict[stream]['queues']['chunks'] = 0
		self.subshells_dict[stream]['queues']['condition'] = Condition()
		self.subshells_dict[stream]['shell'] = subshell_class(stream, self.handler, self.subshells_dict[stream]['queues'], self, self.ignore_messages, **subshell_kwargs )

		self.handler.orchestrator.addStream( stream )


	def default( self, line ) :

		if line.startswith( self.stream_preamp_char ) :
			rest = line[1:]
			command = None
			try :
				tok_len = len( rest.split() )
				if tok_len == 1 :
					stream_name = rest.strip()
				else :
					stream_name, command = rest.split(None, 1)
			except ValueError :
				print "*** Shouldn't Happen ***"
				self.__print_streams()
				return
			if stream_name not in self.availableStreams() :
				self.__print_streams()
				self.updatePrompt()
				return
			if not command :
				self.subshells_dict[stream_name]['shell'].start()	#	should contain a stream name
				return
			else :
				self.subshells_dict[stream_name]['shell'].onecmd( command )



	def do_streams( self, line ) :
		self.__print_streams()

	# Quit keywords
	def do_exit( self, *args ) : return self.do_q( *args )
	def do_quit( self, *args ) : return self.do_q( *args )
	def do_q( self, *args ) : return self.quitPrompt()


	def updatePrompt( self ) :
		self.prompt = self.prompt_templ.format( package = covertutils.__name__, version = covertutils.__version__  )


	def availableStreams(self) :
		return self.subshells_dict.keys()


	def __print_streams( self ) :
		print ( "Available streams:\n	[+] " + '	\n	[+] '.join(self.availableStreams()) )



	def start( self ) :

		# try :
		while True :
			ret = None
			try :
				ret = self.cmdloop()
				# if ret :
				break
			except KeyboardInterrupt :
				self.streamMenu()

	def emptyline( self ) :
		return


	def do_help( self, line ) :
		self.streamCharacterHelp( )

	def streamCharacterHelp( self ) :
		print """
Jump to SubShell:
\t<Ctrl-C>

The '{char}' Character:
\t{char}stream <command> <argument1> <argument2> ...

streams
\tJust prints the available streams

Exit with 'exit', 'quit', 'q'

		""".format(char = self.stream_preamp_char)

	def streamMenu( self ) :
		numb_streams = dict(enumerate( self.availableStreams() ))
		numb_streams[99] = 'Back'

		option = None
		while option not in numb_streams.keys() :
			print
			print "Available Streams:"
			for n, stream in numb_streams.items():
				print "\t[{:2}] - {stream}".format(n, stream = stream)

			try :
				option = int(raw_input( "Select stream: " ))
			except :
				print
				print self.ruler * 20
				pass

		if option == 99 :
			return True
		# 	print "Aborted by user..."
		# 	sys.exit(0)

		selected_stream = numb_streams[option]
		self.subshells_dict[selected_stream]['shell'].start()


	def quitPrompt( self, *args ) :
		# print args
		exit_input = raw_input("[!]\tQuit shell? [y/N] ")
		if exit_input.lower() == 'y' :
			print "Aborted by the user..."
			# sys.exit(0)
			return True
		return False
