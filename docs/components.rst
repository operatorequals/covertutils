Internal Components
===================

Here you can find code snippets from *covertutils* basic internal components.
They are documented under the :mod:`covertutils` pages, but here they will parade in all their glory.

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

.. _streamidentifier_component:


Stream Identification
---------------------

Docs @ :class:`covertutils.orchestration.streamidentifier.StreamIdentifier`

This class is the `OTP provider` for the whole package.

.. code:: python

	>>> from covertutils.orchestration import StreamIdentifier as StreamIdent
	>>>
	>>> streams = ['main','secondary','testing']
	>>>
	>>> id1 = StreamIdent("Pa55phra531", streams)
	>>> id2 = StreamIdent("Pa55phra531", streams, reverse = True)
	>>>
	>>> tag = id1.getIdentifierForStream('main', byte_len=4)
	>>> tag2 = id1.getIdentifierForStream('main', byte_len=4)
	>>> tag3 = id1.getIdentifierForStream('testing', byte_len=4)
	>>>
	>>> tag4 = id1.getIdentifierForStream('secondary', byte_len=2)
	>>>
	>>> id2.checkIdentifier(tag)
	'main'
	>>> id2.checkIdentifier(tag2)
	'main'
	>>> id2.checkIdentifier(tag3)
	'testing'
	>>> id2.checkIdentifier(tag4)
	'secondary'
	>>>
	>>> print (tag, tag2, tag3, tag4)
	('`\xc9\xca\xeb', '\xe8\xf7$\x1f', '\x00\x03\xfa\xaf', 'v\x17')
	>>>
	>>> print (id2.checkIdentifier(tag))
	None

.. _compressor_component:

Compressor
----------

Docs @ :class:`covertutils.datamanipulation.compressor.Compressor`

This class ensures that the data traveling through the wire are as minimal as possible.
It does that by measuring the output of **several compression algorithms**.

Decompression works through *trial & error*.

.. code:: python

>>> from covertutils.datamanipulation import Compressor
>>> from os import urandom
>>>
>>> rand_data = urandom(32)
>>> plain_data = "AB"*16
>>> print rand_data
w!�w`:Ƀ�tU��Jr���?ב�K��lݽ�
>>> print plain_data
ABABABABABABABABABABABABABABABAB
>>>
>>> comp = Compressor()
>>>
>>> comp_rand_data = comp.compress(rand_data)	# Compressing random data is infeasible
>>> print comp_rand_data
w!�w`:Ƀ�tU��Jr���?ב�K��lݽ�
>>> print comp_rand_data == rand_data	# So the returned bytearray is the initial data
True
>>> comp_plain_data = comp.compress(plain_data)	# Compressing repeated text
>>> print comp_plain_data		# Is really efficient though!
x�str�
      �1
>>> print comp_plain_data == plain_data	# So the best compression is returned
False
>>>
>>> print comp.decompress( comp_rand_data )	# The decompression tries all compression schemes
w!�w`:Ƀ�tU��Jr���?ב�K��lݽ�
>>> print comp.decompress( comp_rand_data ) == comp_rand_data
True			# And return the initial data if all of them fail
>>> print comp.decompress( comp_plain_data ) == comp_plain_data
False
>>> print comp.decompress( comp_plain_data ) == plain_data	# But if the data is truly compressed
True			# It returns the decompressed form
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


Steganography Injector
----------------------

Docs @ :class:`covertutils.datamanipulation.stegoinjector.StegoInjector`

The most engineered class in the whole project.

.. code:: python

	>>> from covertutils.datamanipulation import StegoInjector
	>>>
	>>> stego_config = '''
	... X:_data_:
	... Y:_sxor_( chr(_index_), _data_ ):
	...
	... sample1="""4142XXYYXXYY4344"""
	... '''
	>>>
	>>> sinj = StegoInjector(stego_config)
	>>>
	>>> payload = sinj.inject("\x00" * 4, 'sample1')
	>>> print payload.encode('hex')
	4142000300054344
	>>>
	>>> payload2 = sinj.injectByTag( {'X' : '\xff' * 2, 'Y' : '\x00' * 2}, 'sample1')
	>>> print payload2.encode('hex')
	4142ff03ff054344
	>>>
	>>> sinj.extract(payload, 'sample1')
	'\x00\x00\x00\x00'
	>>>
	>>> sinj.extractByTag(payload2, 'sample1')
	{'Y': bytearray(b'\x00\x00'), 'X': bytearray(b'\xff\xff')}
	>>>
	>>> sinj.guessTemplate(payload)
	('sample1', 1.0)		# 	(template_name, possibility)
	>>>


Steganography Packet Templating
-------------------------------

HTTP Protocol Stego
*******************

.. code:: python

	>>> from covertutils.datamanipulation import asciiToHexTemplate
	>>>
	>>> search_request="""GET /search.php?q=~~~~~~~~?userid=~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HTTP/1.1
	... Host: {0}
	... Cookie: SESSIOID=~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	... eTag: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	...
	... """
	>>> search_template = asciiToHexTemplate(search_request)
	>>>
	>>> print search_template
	0a474554202f7365617263682e7068703f713dXXXXXXXXXXXXXXXX3f7573657269643dXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX20485454502f312e310a486f73743a207b307d0a436f6f6b69653a2053455353494f49443dXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX0a655461673a20XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX0a0a
	>>>
	>>> stego_config = """
	... X:_data_:
	... search='''%s'''
	... """ % search_template
	>>>
	>>> from covertutils.datamanipulation import StegoInjector
	>>>
	>>> sinj = StegoInjector(stego_config)
	>>> sinj.getCapacityDict( 'search' )
	{'X': 212}
	>>>
	>>> packet = sinj.inject("A"*212, 'search')
	>>> print packet
	GET /search.php?q=AAAAAAAA?userid=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA HTTP/1.1
	Host: {0}
	Cookie: SESSIOID=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
	eTag: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
	>>>
