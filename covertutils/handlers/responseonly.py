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

		self.preferred_send = self.queueSend


	def onMessage( self, stream, message ) :
		beacon = (message == self.request_data)	# got a beacon message?
		# if beacon :
		# print "List of messages '%s' " % self.to_send_list
		# if not self.readifyQueue() : return False
		self.readifyQueue()
		# print "Raw packets pending: %s" % len(self.to_send_raw)
		if self.to_send_raw :
			to_send = self.to_send_raw.pop(0)
			self.send_function( to_send )
			return True
		return False
