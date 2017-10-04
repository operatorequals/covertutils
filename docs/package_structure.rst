
.. _package_structure :

Package, subpackage and module structure
========================================


This project has been structured using *single-file class approach*. While this is not that *Pythonic* (more like Jav'ish) I find it best for a *heavily Object Oriented Project* like this.

To retain the *Pythonic* import structure, a *class*, say ``Foo``, declared in a module-file, say, ``pack/subpack/mod.py`` can be imported both with:

.. code:: python

	 from pack.subpack.mod import Foo

and

.. code:: python

 	 from pack.subpack import Foo

as all modules happen to contain only **one class each**.

To also borrow some more *Jav'ish* taste, all class names are `camelCased` and have their first letter `Capitalized`, while the modules containing them share the same name but all `lowercase`.

For example, the :class:`covertutils.handlers.basehandler.BaseHandler` class can be imported like:

.. code:: python

	from covertutils.handlers.basehandler import BaseHandler

and like:

.. code:: python

	from covertutils.handlers import BaseHandler

as :mod:`covertutils.handlers.basehandler` only contains the `BaseHandler` class


.. note:: If importing errors like the following happen:

	.. code:: python

		>>> import coverutils
		Traceback (most recent call last):
		  File "<stdin>", line 1, in <module>
		ImportError: No module named coverutils
		>>>

	Be sure to write the `package name` properly:
	It's cover **t** utils.

	It happens all the time to me...
