.. CovertUtils documentation master file, created by
   sphinx-quickstart on Sun Jul 23 17:17:59 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


	 .. moduleauthor:: John Torakis <john.torakis@gmail.com>


Welcome to ``covertutils`` documentation!
=========================================

This Project is free and open-source, available @ Github_

.. _Github : https://github.com/operatorequals/covertutils


A Blog post about it, explaining *motivation* and *implementation internals* can be found in my personal blog: Securosophy_

.. _Securosophy : https://securosophy.com/2017/04/22/reinventing-the-wheel-for-the-last-time-the-covertutils-package/


Not a Backdoor!
---------------

Well, *almost* not a backdoor. This project is a *Python2 package* containing enough modules for implementing custom backdoors.
Everything, from *file transfer* to *customized shells* is included.


It is not a backdoor ready to be planted (well, most of the :ref:`programming_examples` are). If you are looking for backdoors, RATs and such stuff in `Python` there are some awesome projects already:

 - Weevely_
 - Pupy_
 - Stitch_
 - Empire_ (agent also in `PowerShell`)

.. _Weevely : https://github.com/epinna/weevely3
.. _Pupy : https://github.com/n1nj4sec/pupy
.. _Stitch : https://github.com/nathanlopez/Stitch
.. _Empire : https://www.powershellempire.com/


This package contains most **Building Blocks** of a backdoor. It covers the common coding tasks when creating anything from a simple `reverse TCP shell` to a full-blown, feature-rich, extend-able, `Agent`.

It also uses a simplistic approach of what a backdoor is, breaking it down to its basic components:

 - Agent
 - Handler
 - Communication Channel
 - Protocol


Currently, ``covertutils`` package provides API for:

 - Encryption
 - Chunking
 - Separate Streams (almost like `meterpreter`'s channels)
 - Compression before transmission
 - Packet Steganography
 - Customized Shell
 - Message Handling
 - Custom Shell creation

And most of those features are used under the hood, without writing any additional line of code (e.g. `encryption`, `compression`, `streams`).


No Networking code included
---------------------------

The package provides a generic wrapper for networking, without implementing internally even the simplest of networking possibilities (e.g. `bind TCP`).

This design decision broadens the possibilities for `Communication Channels` that differ a lot from just layer 4/5 solutions. This way, there is space for `Packet Steganography` or even time-based `Covert Channels`.

And all that with the abstraction of **Object Oriented Programming**, as this package depends on it heavily.


.. toctree::
 :maxdepth: 1
 :caption: Basics:

 installation
 package_structure
 native_execs

.. toctree::
	:maxdepth: 2
	:caption: Internals:

	components
	architecture
	shells
	stages

.. toctree::
	:maxdepth: 2
	:caption: Techniques:

	ids_evasion
	staging_exec

.. toctree::
	:maxdepth: 2
	:caption: Tutorial'ish Material:

	assembling_backdoor
	prog_examples
	stage_api
	real_covert_channel_pozzo_n_lucky


All modules *[citation needed]* are documented automatically from comments with *Sphinx* ``apidoc``. The output is below...

.. toctree::
 :maxdepth: 3
 :caption: The whole "apidoc" pages ahead:

 modules




As the *covertutils API* Toc-Tree is **huge** (due to the code organizing, see: :ref:`package_structure`), it is really handy to use the **search page** of **Sphinx** if you are looking for a specific `class` or `method`.





.. note:: For `flawless backdoor creation` don't forget to fire up some Primus CDs or old blues standards while coding. Maybe light a cigar too.


.. note:: Creating stealthy backdoors requires intelligence, and intelligence is **a terrible thing to waste**.
