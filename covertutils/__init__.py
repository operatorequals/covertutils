"""
The `covertutils` module provides ready plug-n-play tools for `Remote Code Execution Agent` programming.
Features like `chunking`, `encryption`, `data identification` are all handled transparently by its classes.
The :class:`SimpleOrchestrator` handles all data manipulation, and the :class:`Handlers.BaseHandler` derivative classes handle the agent's and handler's actions and responses.

The module does not provide networking functionalities. All networking has to be wrapped by two functions (a sender and a receiver functions) and Handlers will use those for raw_data

Programming Examples:
=====================
In all examples Encryption and Chunking are build-in features.

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




Packet Hex Dump ( `ls` command and response )::

    06:50:23.541910 IP 127.0.0.1.53676 > 127.0.0.2.8012: Flags [S], seq 4049783139, win 43690, options [mss 65495,sackOK,TS val 58905769 ecr 0,nop,wscale 7], length 0
    ..............E..<..@.@..............L.b.c.........1.........
    ............
    06:50:23.541921 IP 127.0.0.2.8012 > 127.0.0.1.53676: Flags [S.], seq 178116363, ack 4049783140, win 43690, options [mss 65495,sackOK,TS val 58905769 ecr 58905769,nop,wscale 7], length 0
    ..............E..<..@.@.<..........L..
    ....b.d.....1.........
    ............
    06:50:23.541929 IP 127.0.0.1.53676 > 127.0.0.2.8012: Flags [.], ack 1, win 342, options [nop,nop,TS val 58905769 ecr 58905769], length 0
    ..............E..4..@.@..............L.b.d
    ......V.).....
    ........
    06:50:24.927298 IP 127.0.0.1.53676 > 127.0.0.2.8012: Flags [P.], seq 1:51, ack 1, win 342, options [nop,nop,TS val 58906115 ecr 58905769], length 50
    ..............E..f..@.@..............L.b.d
    ......V.[.....
    ........".D.L{.....G.tve.,....u....q.!.".v7.{...6.>....OQ2
    06:50:24.927497 IP 127.0.0.2.8012 > 127.0.0.1.53676: Flags [.], ack 51, win 342, options [nop,nop,TS val 58906116 ecr 58906115], length 0
    ..............E..4..@.@.9..........L..
    ....b.....V.).....
    ........
    06:50:24.931759 IP 127.0.0.2.8012 > 127.0.0.1.53676: Flags [P.], seq 1:51, ack 51, win 342, options [nop,nop,TS val 58906117 ecr 58906115], length 50
    ..............E..f..@.@.8..........L..
    ....b.....V.[.....
    ........"..0(.9...AE.......>;m......3.M*2..f.S.R..>....OI.
    06:50:24.931772 IP 127.0.0.1.53676 > 127.0.0.2.8012: Flags [.], ack 51, win 342, options [nop,nop,TS val 58906117 ecr 58906117], length 0
    ..............E..4..@.@..............L.b..
    ..>...V.).....
    ........
    06:50:26.630345 IP 127.0.0.1.53676 > 127.0.0.2.8012: Flags [F.], seq 51, ack 51, win 342, options [nop,nop,TS val 58906541 ecr 58906117], length 0
    ..............E..4..@.@..............L.b..
    ..>...V.).....
    ........
    06:50:26.672055 IP 127.0.0.2.8012 > 127.0.0.1.53676: Flags [.], ack 52, win 342, options [nop,nop,TS val 58906552 ecr 58906541], length 0
    ..............E..4..@.@.9..........L..
    ..>.b.....V.).....
    ........

Notice: All data packets (PUSH flag) have a payload of exactly 50 bytes, which is encrypted with One-Time-Pad algorithm described in :class:`PseudoOTP.OTPKey`.
"""

__version__ = '0.0.2'
__name__ = 'covertutils'
__author__ = 'John Torakis - operatorequals'
__email__ = 'john.torakis@gmail.com'
__github__ = 'https://github.com/operatorequals/covertutils'
__readthedocs__ = 'https://covertutils.readthedocs.io'
