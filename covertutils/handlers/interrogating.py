from time import sleep

from abc import ABCMeta, abstractmethod

from covertutils.helpers import defaultArgMerging
from covertutils.handlers import BaseHandler

from threading import Thread

from random import uniform


class InterrogatingHandler( BaseHandler ) :
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
		super(InterrogatingHandler, self).__init__( recv, send, orchestrator, **kw )

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

			self.readifyQueue()
			while not self.to_send_raw :
				self.queueSend( self.request_data, self.fetch_stream )
				self.readifyQueue()

			to_send = self.to_send_raw.pop(0)
			self.send_function( to_send )
