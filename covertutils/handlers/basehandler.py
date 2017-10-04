from abc import ABCMeta, abstractmethod
# from time import sleep
from threading import Thread

from covertutils.helpers import defaultArgMerging



class BaseHandler :
	"""
Subclassing this class and overriding its methods automatically creates a threaded handler.
"""

	__metaclass__ = ABCMeta
 	Defaults = {
		'start' : True,
	}

	def __init__( self, recv, send, orchestrator, **kw ) :
		"""
:param `function` recv: A **blocking** function that returns every time a chunk is received. The return type must be raw data, directly fetched from the channel.
:param `function` send: A function that takes raw data as argument and sends it across the channel.
:param `orchestration.SimpleOrchestrator` orchestrator: An Object that is used to translate raw data to `(stream, message)` tuples.
		"""
		# print (kw)
 		arguments = defaultArgMerging( BaseHandler.Defaults, kw )
		# print (arguments)
		self.receive_function = recv
		self.send_function = send
		self.orchestrator = orchestrator

		self.preferred_send = self.sendAdHoc

		self.to_send_list = []
		self.to_send_raw = []

		self.__protocolThread = Thread( target = self.__protocolThreadFunction )
		self.__protocolThread.daemon = True

		self.on = True
 		if arguments['start'] :
 			self.start()


 	def start( self ) :
		'''
Starts the thread that consumes data and enables the `on*` callback methods.
		'''
 		self.__protocolThread.start()


 	def stop( self ) :
		'''
Stops the handler thread making the data consumer to return (if not blocked).
		'''
 		self.on = False


	def queueSend( self, message, stream = None ) :
		"""
:param str message: The message that will be stored for sending upon request.
:param str stream: The stream where the message will be sent.
"""
		if stream == None :
			stream = self.orchestrator.getDefaultStream()
		self.to_send_list.append( (message, stream) )


	def readifyQueue( self ) :

		if self.to_send_list :
			message, stream = self.to_send_list.pop(0)
			chunks = self.orchestrator.readyMessage( message, stream )
			self.to_send_raw.extend( chunks )
			return True
		return False



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
This method uses the object's `SimpleOrchestrator` instance to send raw data to the other side, throught the specified `Stream`.
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

		while self.on :
			raw_data = self.receive_function()
			stream, message = self.orchestrator.depositChunk( raw_data )
			message_consumer = Thread( target = self.__consume, args = ( stream, message ) )
			message_consumer.daemon = True
			message_consumer.start()
			# self.__consume( stream, message )


	def getOrchestrator( self ) :
		"""

:rtype: `Orchestrator`
:return: Returns the Orchestrator object used to create this `Handler` instance.

		"""
		return self.orchestrator


	def reset( self ) :
		self.orchestrator.reset()
		self.to_send_list = []
		self.to_send_raw = []


	def addStream( self, stream ) :
		self.orchestrator.addStream( stream )
		return stream
