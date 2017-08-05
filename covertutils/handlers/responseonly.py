from abc import ABCMeta, abstractmethod

from covertutils.handlers import BaseHandler

from covertutils.helpers import defaultArgMerging


class ResponseOnlyHandler( BaseHandler ) :
	"""
This handler doesn't send messages with the `sendAdHoc` method. It implements a method `queueSend` to queue messages, and send them only if it is queried with a `request_data` message.

Can be nicely paired with :class:`covertutils.handlers.InterrogatingHandler` for a Client-Server approach.
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
