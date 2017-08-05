from abc import ABCMeta, abstractmethod

from covertutils.handlers import BaseHandler

from covertutils.payloads import CommonStages
from covertutils.helpers import defaultArgMerging


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
