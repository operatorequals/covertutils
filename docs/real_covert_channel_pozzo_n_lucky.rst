
.. _pozzo_n_lucky :

Pozzo & Lucky
=============

Some References First
---------------------

The Blog Posts that started all
*******************************

* `The Basic Idea and PoC`__

.. _part1 : https://securosophy.com/2016/09/14/teaching-an-old-dog-not-that-new-tricks-stego-in-tcpip-made-easy-part-1/

__ part1_



* `The Implementation requirements and Demo`__


.. _part2 : https://securosophy.com/2016/09/19/pozzo-lucky-stego-in-tcpip-part-2/

__ part2_


* `The Mitigation Research`__

.. _part3 : https://securosophy.com/2016/09/28/pozzo-lucky-busted-the-tales-of-a-mathematician-soc-analyst/

__ part3_

Parts of these articles have been republished in exploit-db_ and shellstorm_.
They 've also been translated_.

Finally, it seems that another project_ has been based on them.


**People like backdoors!**

.. _exploit-db: https://www.exploit-db.com/docs/english/40891-teaching-an-old-dog-(not-that-new)-tricks.-stego-in-tcpip-made-easy-(part-1).pdf
.. _shellstorm: https://packetstormsecurity.com/files/140115/Pozzo-And-Lucky-The-Phantom-Shell.-Stego-In-TCP-IP-Part-2.html
.. _translated: https://www.securitylab.ru/analytics/485960.php?R=1
.. _project: https://habrahabr.ru/post/332962/

The Case of a Real Covert Channel
---------------------------------

*Or the day when C2 (Command & Control) became C4 (Covert Channel Command & Control)*

It's been more than a year since I published the posts of *Pozzo & Lucky*.
A backdoor that can operate fully using **IP/TCP headers to hide its payloads**,
while granting total command execution to the *Handler*


The whole communication between the *Agent* and the *Handler* resembled a port scan
like a reoccurring ``nmap -sS <AgentIP> -Pn``,
with the *Agent* responding with ``RST, ACK`` for all packets.

The communication was IP independent, so the *Handler* could switch IPs midways,
to try and prevent being spotted and blacklisted as a *Scanner IP*,
while *Agent* would still recognize the same *Handler* regardless of the *Source Address*.

This all sounds good now and sounded better when I published *but*:

*I never published the code*
----------------------------

The code of this project was so much spaghetti that I was ashamed of myself for being the author...
So I, didn't publish it. Yet, while trying to refactor this exact code, I came up with the idea of ``covertutils``.
Avoiding ``Scapy`` dependencies, managing compression for super low tunnel bandwidths
and :ref:`ids_evasion` were ideas from *Pozzo & Lucky*.

So, now the ``covertutils`` project became mature enough to manage a **whole re-write**
of the *Pozzo & Lucky* backdoor with **only covertutils dependency** and *pure Python2*.

Some readers were displeased that I didn't publish even later (while I said that I'd do).
This was a common case where code refactoring took a year... It happens.

**Until now...**
----------------

The Concept
***********

Installing *Lucky* (the *Agent*) to any Internet facing host could make it obey to remote commands
without raising any suspicion through ``netstat``/``lsof -i`` and the alike (as no connection is really made)
or make itself visible through beacons leaving the host.
It does not rely to standard binary patches like *SSH Server dual password login* or
*Apache module backdoors*.

The commands are received by parsing ``IP Identification Field``, ``TCP Sequence Numbers`` and ``Source Ports``.
The responses are sent by cooking new packets with the payloads attached to the same fields.
The *TCP protocol* isn't violated **in any way**, so IDS signatures are sure to not trigger!

The Setup
*********

This is a **Linux Only** backdoor.
Both *Pozzo* and *Lucky* need ``root`` or the raw socket capability to run.
Packets are sniffed from Layer 2, so host Firewalls do not block it by design.
*Lucky* and ``iptables`` read from the same source (kinda).



The Code
********

Fully commented and as self-explanatory as I could.


StegoInjector Configuration
++++++++++++++++++++++++++++++++++

Not needed, as it is hardcoded in both sides, but useful to be listed separately.
It utilizes the agnostic parsing capabilities of :class:`covertutils.datamanipulation.stegoinjector.StegoInjector` class
to inject payload to IP/TCP packets.


.. literalinclude:: ../examples/pozzo_n_lucky/stego_config.py


Agent - Server (*Lucky*)
+++++++++++++++++++++++++

.. literalinclude:: ../examples/pozzo_n_lucky/lucky.py



Handler - Client (*Pozzo*)
++++++++++++++++++++++++++

.. literalinclude:: ../examples/pozzo_n_lucky/pozzo.py



Traffic Samples
---------------

A ``shell`` Command
*******************

This is not a Port Scan...

.. code ::

	# tcpdump -i lo
	tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
	listening on lo, link-type EN10MB (Ethernet), capture size 262144 bytes
	13:33:56.253722 IP localhost.45159 > 127.0.0.5.1037: Flags [S], seq 4103998434, win 8192, length 0
	13:33:56.626803 IP 127.0.0.5.1037 > localhost.45159: Flags [R.], seq 3127931674, ack 4103998435, win 8192, length 0
	13:33:56.632483 IP localhost.25508 > 127.0.0.5.1036: Flags [S], seq 1970724636, win 8192, length 0
	13:33:56.636883 IP 127.0.0.5.1036 > localhost.25508: Flags [R.], seq 967199669, ack 1970724637, win 8192, length 0
	[...]
	13:33:58.690345 IP localhost.51155 > 127.0.0.5.20005: Flags [S], seq 3525466464, win 8192, length 0
	13:33:58.695351 IP 127.0.0.5.20005 > localhost.51155: Flags [R.], seq 3362657208, ack 3525466465, win 8192, length 0
	13:33:58.701801 IP localhost.44898 > 127.0.0.5.6969: Flags [S], seq 3759950108, win 8192, length 0
	13:33:58.706217 IP 127.0.0.5.6969 > localhost.44898: Flags [R.], seq 3798515646, ack 3759950109, win 8192, length 0
	13:33:58.712853 IP localhost.3721 > 127.0.0.5.vopied: Flags [S], seq 3966697458, win 8192, length 0
	13:33:58.717565 IP 127.0.0.5.vopied > localhost.3721: Flags [R.], seq 2172710336, ack 3966697459, win 8192, length 0

	384 packets captured
	768 packets received by filter
	0 packets dropped by kernel


This is an ``ls`` command:


.. code ::


	(covertutils v0.3.4)> :os-shell ls
	3c7612c2a4480ef0.os-shell:
	0d415f6ba85c604d
	1fabdd231e2212d8
	501c7894ec04fd11
	5b23ffcdb5320e0a
	a5d74224f04264ac
	aa
	covertutils
	covertutils.egg-info
	dist
	docs
	entropy_read.py
	examples
	execs_demo
	htmlcov
	inmem_zip_importer.obf.py
	inmem_zip_importer.py
	lala7.py
	lala.py
	makefile
	MANIFEST
	MANIFEST.in
	manual_testbed.py
	meterpreter.bare.py
	meterpreter.min.py
	meterpreter.obf.gz.py
	meterpreter.obf.py
	meterpreter.py
	meterpreter_stage.py
	meterpreter_strip_transport.py
	meterpreter_transl.py
	nano.save
	ntpkey_cert_hostname
	ntpkey_host_hostname
	ntpkey_RSAhost_hostname.3724672175
	ntpkey_RSA-MD5cert_hostname.3724672175
	ntp_traffic.pcapng
	ntp_with_apple.pcapng
	README.md
	requirements.txt
	sc_exec.py
	sc.py
	setup.py
	target.pyz
	tests
	test_SimpleMultiHandler.py
	tox.ini

Some transmitted payloads for ``ls`` in ``hex``

.. code::

	4403542dbd9eb9c0
	360d888af5561fc0
	8649df27929a3300
	a4392b406e1683fe
	d8199bf6cd8c7d3e
	f68de4d5cbdebbc2
	9c81e7ac5ecc95d0
	d471e92efea6d1fa
	e8c54d8e5656770e
	ac5f282023c4b782
	4ee7cc27f9c4b9f8



A ``wireshark`` screenshot *is worth a thousand* ``tcpdump`` lines
******************************************************************

|wireshark|


.. |wireshark| image:: https://github.com/operatorequals/covertutils/raw/master/docs/images/pozzo_n_lucky_traffic.png
