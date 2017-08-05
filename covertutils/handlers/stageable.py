from abc import ABCMeta, abstractmethod

import marshal, types

from covertutils.handlers import BaseHandler, FunctionDictHandler

from covertutils.payloads import CommonStages
from covertutils.helpers import defaultArgMerging


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
