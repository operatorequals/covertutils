Components
===========

Here you can find code snippets from `covertutils` basic internal components.
They are documented under the :ref:`covertutils` pages, but here they will parade in all their glory.

Their understanding is essential in case you want to create a new Orchestrator (:class:`covertutils.orchestration.orchestrator.Orchestrator`) class, or generally tinker with the internals.


The Cycling Algorithm
----------------------

Docs @ :class:`covertutils.crypto.algorithms.standardcyclingalgorithm.StandardCyclingAlgorithm`

.. code:: python

	>>> from covertutils.crypto.algorithms import StandardCyclingAlgorithm as calg
	>>>
	>>> calg("A")				# Has the same API as the hashlib classes
	<covertutils.crypto.algorithms.standardcyclingalgorithm.StandardCyclingAlgorithm object at 0x7f18034c44d0>
	>>> calg("A").hexdigest()
	'b1d841411463be057db1af5f41be284ebe6c144e9c2739415f93af7d7d5f417d'
	>>> calg("A", length = 10).hexdigest()
	'8d7d82938db18db15feb'
	>>> calg("A", length = 10, cycles = 20).hexdigest()
	'8d7d82938db18db15feb'		# "cycles = 20" is the default argument value
	>>> calg("A", length = 10, cycles = 21).hexdigest()
	'b15ff5fa1b41c9273993'
	>>> calg("B", length = 10, cycles = 21).hexdigest()
	'6fc5096f819081719f9f'
	>>>

Yet this algorithm is not a Secure Hasher, as it can contain collisions. It is only used for Cycling Key implementation



The Cycling Key
----------------

Docs @ :class:`covertutils.crypto.keys.standardcyclingkey.StandardCyclingKey`

The Key cycles with every encryption/decryption making it impossible to decrypt the same ciphertext twice.

This makes it an efficient One-Time-Pad Scheme.

.. code ::

	>>> from covertutils.crypto.keys import StandardCyclingKey as ckey
	>>>
	>>> key1 = ckey("SecretPassphrase")
	>>> key2 = ckey("SecretPassphrase")
	>>> message = "A"*100
	>>>
	>>> encr1 = key1.encrypt(message)	# Encrypting the message with Key1
	>>> print encr1.encode('hex')
	00e8b5dd97ffff87324686f21ee1b5e10f4b1100b4442c1cccba76ec22ee003a840eb87b2974a421a6e31cec7b752f1d7bd1b8120220ed30236049a1c156fcde3ed02ecedf03a38902a61054ba5bdd016ac3fe01f13198b6565bab9bf11f0f0a2e122e7b
	>>>
	>>> print key2.decrypt(encr1)
	AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
	>>>
	>>> key1 = ckey("SecretPassphrase")	# Resetting Key1 breaks sync with Key2
	>>> encr1 = key1.encrypt(message)
	>>> print key2.decrypt(encr1)		# Key2 is ahead of Key1 as it has cycled in the previous decryption.
	Y<]��;�E���~L��}:M��7���=%!��킿��lZi��ù�A{�A���U4�	?E��!!E��/��v1
	K���/}�oe�|�8�
	>>>


Stream Identification
---------------------

Docs @ :class:`covertutils.orchestration.streamidentifier.StreamIdentifier`


.. code:: python

	>>> streams = ['main', 'secondary']
	>>> id1 = sident("passphrase", streams)
	>>>
	>>> id2 = sident("passphrase", streams, reverse = True)
	>>>
	>>> id1.getStreams()	# There is always a hard-coded stream for safety reasons
	['control', 'main', 'secondary']
	>>>
	>>> tag = id1.getIdentifierForStream('main', byte_len=4)
	>>>
	>>> tag
	'\x1e\xf33_'	# it is 4 bytes: \x1e,\xf3, 3, _
	>>>
	>>> id2.checkIdentifier(tag)
	'main'
	>>>



Compressor
----------

Docs @ :class:`covertutils.datamanipulation.compressor.Compressor`

.. code:: python

	>>> from covertutils.datamanipulation import Compressor
	>>> comp = Compressor()
	>>> message = "A"*100
	>>>
	>>> compressed = comp.compress(message)
	>>> print compressed
	x�st�=�e
	>>> comp.decompress(compressed)
	'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
	>>>



Chunker
--------

Docs @ :class:`covertutils.datamanipulation.chunker.Chunker`

.. code:: python

	>>> from covertutils.datamanipulation import Chunker
	>>>
	>>> ch1 = Chunker( 10, 5 )
	>>> ch2 = Chunker( 10, 5, reverse = True )
	>>>
	>>> message = "A"*100
	>>>
	>>> ch1.chunkMessage( message )	# 10 bytes each chunk, with delimiter.
	['\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x01A\xe8\xfce\xe2\r\xd6\xb9t']
	>>>	# The last chunk contains random padding
	>>>
	>>> chunks = ch1.chunkMessage( message )
	>>> print chunks
	['\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x00AAAAAAAAA', '\x01A\xa8\x8e\xa2\xf7v"\xb6/']
	>>>
	>>> for chunk in chunks :
	...     ch2.deChunkMessage( chunk )
	...
	(None, None)
	(None, None)
	(None, None)
	(None, None)
	(None, None)
	(None, None)
	(None, None)
	(None, None)
	(None, None)
	(None, None)
	(None, None)
	(True, 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
	>>>
