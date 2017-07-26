
from time import sleep

from abc import ABCMeta, abstractmethod

from covertutils.helpers import defaultArgMerging
from covertutils.handlers import BaseHandler




class ResettableHandler ( BaseHandler ) :
	"""
This handler can reset the :class:`covertutils.orchestration.SimpleOrchestrator` object (reset all crypto keys, stream identifiers, chunkers), in case the state between the agent and handler is lost.

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
		self.preferred_send( ResettableHandler.Defaults[reset_data] )


	def onMessage( self, stream, message ) :
		if message == self.reset_data :
			self.reset()
			return True
		return False
