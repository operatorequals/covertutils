
.. _pozzo_n_lucky :

Pozzo & Lucky
=============

Some References First
---------------------

The Blog Posts that started all
******************************

* The Basic Idea and PoC


https://securosophy.com/2016/09/14/teaching-an-old-dog-not-that-new-tricks-stego-in-tcpip-made-easy-part-1/


* The Implementation requirements and Demo

https://securosophy.com/2016/09/19/pozzo-lucky-stego-in-tcpip-part-2/

* The Mitigation Research

https://securosophy.com/2016/09/28/pozzo-lucky-busted-the-tales-of-a-mathematician-soc-analyst/

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

Some readers were displeased that I didn't published (while I said that I'd do).
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
