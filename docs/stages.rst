Beyond the OS Shell
===================

The `covertutils` package has an API for creating custom stages that can be dynamically loaded to compromised machines.
If a :class:`covertutils.handlers.stageable.StageableHandler` is running in a pwned machine stages can be pushed to it.

The API is documented in the `payloads` section (under construction).

Some stages are demonstrarted in this page.


The Python Stage
----------------

A Python shell with access to all internals is available.

The sent code runs directly in the `covertutils stage API`,
so it is able to access the `storage` and `storage['COMMON']` dictionaries and change internals objects at runtime.

.. code:: bash

	(covertutils v0.2.1)[control]> !python
	(covertutils v0.2.1)[python]>
	(covertutils v0.2.1)[python]> print "This is Python code!"
	This is Python code!

	(covertutils v0.2.1)[python]> print "It is Executed in Agent"
	It is Executed in Agent

	(covertutils v0.2.1)[python]> print "It has access to all internals at runtime"
	It has access to all internals at runtime

	(covertutils v0.2.1)[python]> print "Like the '%s' object" % (str(storage['COMMON']['handler'])	# It compiles and returns syntactical error
	unexpected EOF while parsing (<string>, line 1)			# Notice the parenthesis!

	(covertutils v0.2.1)[python]> print "Like the '%s' object running right now!" % (str(storage['COMMON']['handler']))

	Like the '<__main__.AgentHandler object at 0x7f42596c1d90>' object running right now!

	(covertutils v0.2.1)[python]> storage['whatever'] = "You can also store things in 'storage' dict"
	(covertutils v0.2.1)[python]>
	(covertutils v0.2.1)[python]> print storage['whatever']
	You can also store things in 'storage' dict

	(covertutils v0.2.1)[python]> print "It can modify things at runtime!"
	It can modify things at runtime!

	(covertutils v0.2.1)[python]> storage['COMMON']['handler'].send_function = None
	(covertutils v0.2.1)[python]>
	(covertutils v0.2.1)[python]> print "Nulled the send function, the Agent will remain silent..."
	(covertutils v0.2.1)[python]> Exception in thread Thread-67:
	Traceback (most recent call last):
	  File "/usr/lib/python2.7/threading.py", line 801, in __bootstrap_inner
	    self.run()
	  File "/usr/lib/python2.7/threading.py", line 754, in run
	    self.__target(*self.__args, **self.__kwargs)
	  File "/home/unused/Projects/covertutils/covertutils/handlers/basehandler.py", line 69, in __consume
	    self.onMessage( stream, message )
	  File "manual_testbed.py", line 62, in onMessage
	    self.preferred_send(ret)
	  File "/home/unused/Projects/covertutils/covertutils/handlers/basehandler.py", line 138, in sendAdHoc
	    self.send_function( chunk )
	TypeError: 'NoneType' object is not callable

	(covertutils v0.2.1)[python]>
	(covertutils v0.2.1)[python]>
	Really Control-C [y/N]? y
	Aborted by the user...
