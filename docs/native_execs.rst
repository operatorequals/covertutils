.. _native_execs_page :

Native Executables
==================

Generating **Native Executables** for all platforms is major feature for backdoors!
Those will be your payloads in **Phishing emails** and **USB drive Parking-Ops** after all!


Currently `Linux` and `Windows` are directly supported through PyInstaller_.

The repo's makefile has options for one-line *exe* generation. Get the latest repo's *makefile script* from here_.

**or just:**

.. code:: bash

	wget https://raw.githubusercontent.com/operatorequals/covertutils/master/makefile

.. _here: https://github.com/operatorequals/covertutils
.. _PyInstaller: http://www.pyinstaller.org/index.html



Linux
*****

For a **script** name of ``backdoor_script.py`` and **executable** name of ``.sshd`` type the following:

.. code:: bash

 	make PY='backdoor_script.py' EX='.sshd' elf



Windows
*******

You will need the whole *wine - Python2.7 - PyInstaller* toolchain assuming that you are running *Linux*.

For a **script** name of ``backdoor_script.py`` and **executable** name of ``crazy_taxi_crack_2.34.exe`` type the following:

.. code:: bash

	make PY='backdoor_script.py' EX='crazy_taxi_crack_2.34.exe' exe



Several other packers for Python to native **dependency-less** executables are in the wild.
You can try :

- py2exe_
- nuitka_	(tends to create executables much smaller than `PyInstaller`'s)


If you've found a configuration that works best for you (like: "*I use XYZ with ABC and create super small executables*"), please open an Issue in the Github repo_ and I will add it to the defaults.


.. _py2exe: http://www.py2exe.org/
.. _nuitka: http://nuitka.net/
.. _repo: https://github.com/operatorequals/covertutils/issues


Have fun *responsibly*!
