Beyond the OS Shell
===================

The `covertutils` package has an API for creating custom stages that can be dynamically loaded to compromised machines.
If a :class:`covertutils.handlers.stageable.StageableHandler` is running in a pwned machine stages can be pushed to it.

The API is documented in the `payloads` section (under construction).

Some stages are demonstrarted in this page.


.. _pythonapi-stage:

The Python Stage
----------------

A Python shell with access to all internals is available.

The sent code runs directly in the `covertutils stage API`,
so it is able to access the `storage` and `storage['COMMON']` dictionaries and change internals objects at runtime.

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
