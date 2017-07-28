# from abc import ABCMeta, abstractmethod
from covertutils.exceptions import *
from covertutils.handlers import BaseHandler

from covertutils.helpers import defaultArgMerging

import marshal, types

from threading import Thread
# from multiprocessing import Queue
from Queue import Queue


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

	from covertutils.payloads import GenericStages
	pprint( GenericStages )
	{'shell': {'function': <function __system_shell at 0x7fc347472320>,
		   'marshal': 'c\\x01\\x00\\x00\\x00\\x03\\x00\\x00\\x00\\x02\\x00\\x00\\x00C\\x00\\x00\\x00s&\\x00\\x00\\x00d\\x01\\x00d\\x02\\x00l\\x00\\x00m\\x01\\x00}\\x01\\x00\\x01|\\x01\\x00|\\x00\\x00\\x83\\x01\\x00j\\x02\\x00\\x83\\x00\\x00}\\x02\\x00|\\x02\\x00S(\\x03\\x00\\x00\\x00Ni\\xff\\xff\\xff\\xff(\\x01\\x00\\x00\\x00t\\x05\\x00\\x00\\x00popen(\\x03\\x00\\x00\\x00t\\x02\\x00\\x00\\x00osR\\x00\\x00\\x00\\x00t\\x04\\x00\\x00\\x00read(\\x03\\x00\\x00\\x00t\\x07\\x00\\x00\\x00messageR\\x00\\x00\\x00\\x00t\\x06\\x00\\x00\\x00result(\\x00\\x00\\x00\\x00(\\x00\\x00\\x00\\x00s\\x15\\x00\\x00\\x00covertutils/Stages.pyt\\x0e\\x00\\x00\\x00__system_shell\\x04\\x00\\x00\\x00s\\x06\\x00\\x00\\x00\\x00\\x01\\x10\\x01\\x12\\x01'}}

	"""

	# __metaclass__ = ABCMeta

	def __init__( self,  recv, send, orchestrator, **kw ) :
		"""
:param dict function_dict: A dict containing `(stream_name, function)` tuples. Every time a message is received from `stream_name`, `function(message)` will be automatically executed.
		"""
		super( FunctionDictHandler, self ).__init__( recv, send, orchestrator, **kw )
		self.stage_storage = {}
		self.stage_storage['COMMON'] = {}
		self.stage_storage['COMMON']['handler'] = self
		self.processed_responses = Queue()
		# try :
			# self.function_dict = kw['function_dict']
		for stream, stage in kw['function_dict'].items() :
			self.addStage( stream, stage )

		# except :
		# 	raise NoFunctionAvailableException( "No Function dict provided to contructor" )


	def onMessage( self, stream, message ) :
		"""
:raises: :exc:`NoFunctionAvailableException`
		"""
		super( FunctionDictHandler, self ).onMessage( stream, message )
		# print message
		self.stage_storage[stream]['queue'].put( message )
		# print "Put to Queue"
		ret = self.processed_responses.get(True)
		# print "Processed: "+ret
		return ret

	def onChunk( self, stream, message ) : pass
	def onNotRecognised( self ) : pass


	def stageWorker( self, init, worker, storage ) :
		# print "Handler: Worker Started"
		if not init(storage) : return
		# print "Handler: Init Run Started"
		while storage['on'] :
			# print "Try to GET from Queue"
			message = storage['queue'].get( block = True )
			# print "Handler: Work() Run"
			ret = worker(storage, message)
			# print ret, type(ret)
			self.processed_responses.put( ret )
		self.stage_storage[stream] = {}


	def getStage( self, stage_obj ) :

		# Recognize the type of stage

		# Assume 'marshal' for now
		stage_dict = marshal.loads( stage_obj )
		# print  stage_dict
		# print  stage_dict['init']
		if stage_dict['init'] == None :
			stage_init = _dummy_init
		else :
			stage_init = types.FunctionType(stage_dict['init'], globals(), "stage_init_func")
		stage_work = types.FunctionType(stage_dict['work'], globals(), "stage_work_func")
		# print  stage_init
		return stage_init, stage_work


	def addStage( self, stream, stage_obj ) :

		self.stage_storage[stream] = {}
		self.stage_storage[stream]['queue'] = Queue()
		self.stage_storage[stream]['on'] = True
		self.stage_storage[stream]['COMMON'] = self.stage_storage['COMMON']
		# print stream
		stage_init, stage_worker = self.getStage( stage_obj )
		self.orchestrator.addStream( stream )

		stage_thread = Thread( target = self.stageWorker, args = ( stage_init, stage_worker, self.stage_storage[stream] ) )
		stage_thread.daemon = True
		stage_thread.start()
		pass


def _dummy_init (storage) :
	return True
