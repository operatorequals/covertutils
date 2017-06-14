
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
To

Wireshark HTTP stream
*********************


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
