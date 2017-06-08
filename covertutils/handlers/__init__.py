"""
This module provides a template for Automatic protocol creation.
The base class :class:`covertutils.handlers.BaseHandler` provide an API with methods:

 - onChunk()
 - onMessage()
 - onNotRecognized()

Subclassing the `BaseHandler` class needs an implementation of the above methods.

.. code:: python

	from covertutils.handlers import BaseHandler

	class MyHandler( BaseHandler ) :

		def onMessage( self, stream, message ) :
			print "Got Message '%s' from Stream %s" % ( stream, message )

		def onChunk( self, stream, message ) :
			print "Got Chunk from Stream %s" % ( stream, message )
			if message != '' :
				print "This was the last chunk of a message"

		def onNotRecognised( self ) :
			print "Got Garbage Data"

Creating a `MyHandler` Object needs 2 wrapper functions for raw data **sending** and **receiving**.
The receiving function needs to be **blocking**, just like :func:`socket.socket.recv`
Also a :class:`covertutils.orchestration.SimpleOrchestrator` object is required to handle data chunking, compression and encryption.

.. code:: python

	passphrase = "Th1s1sMyS3cr3t"
	orch = SimpleOrchestrator( passphrase, tag_length = 2, out_length = 50, in_length = 50 )

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect( addr )

	def recv () :
		return s.recv(50)

	def send( raw ) :
		return s.send( raw )

	handler_obj = MyHandler( recv, send, orch )


Then it is possible to send `messages` to other `Handler` instances using the `sendAdHoc()` method.

.. code:: python

	handler_obj.sendAdHoc( "Hello from me" )

Everytime a message is received, the overriden `onMessage()` method will run.

For the Handler at the other side of the channel, to properly decrypt and handle the binary sent by `handler_obj` it is needed to be instantiated with the :func:`covertutils.orchestration.SimpleOrchestrator.__init__` argument ""**reverse = True**""

.. code:: python

	passphrase = "Th1s1sMyS3cr3t"
	orch2 = SimpleOrchestrator( passphrase, tag_length = 2, out_length = 50, in_length = 50, reverse = True )

	handler_obj2 = MyHandler( recv2, send2, orch2 )


The `Handler` Classes are designed for **Multiple Inheritance** for further flexibility.
For instance a Querying, Stageable agent can be implemented like below:

.. code:: python

	from covertutils.handlers import InterrogatingHandler, StageableHandler

 	class MyHandler2( InterrogatingHandler, StageableHandler ) :

		def __init__( self, recv, send, orch, **kw ) :
			super( MyHandler, self ).__init__( recv, send, orch, **kw )

		def onChunk( self, stream, message ) :pass
		def onNotRecognised( self ) :pass

Now, creating a `MyHandler2` object needs the 3 standard arguments (inherited from :func:`covertutils.handlers.BaseHandler.__init__`), and all optional arguments that are needed by the provided `Parent Classes`.

"""



from covertutils.handlers.basehandler import BaseHandler

from covertutils.handlers.functiondict import FunctionDictHandler

from covertutils.handlers.interrogating import InterrogatingHandler

from covertutils.handlers.responseonly import ResponseOnlyHandler

from covertutils.handlers.resettable import ResettableHandler

from covertutils.handlers.stageable import StageableHandler

from covertutils.handlers.buffering import BufferingHandler
