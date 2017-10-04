
.. _ids_evasion:

Totally IDS/IPS evading payloads
================================

Whatever travels from and to ``Handler`` classes is generated using ``Orchestrator`` instances. That means that, not only the communication is encrypted, but there are no `moving parts` on what is transmitted too (`I will elaborate`).


`No-Duplicate` Principle
------------------------

For making the protocol payloads hard to identify I implemented what (I self named) the `No-Duplicate` principle.

This assures that every two consecutive payloads (or more in fact) have the same bytes in same position with a probability of `1/512` (i.e. completely randomly).

In plain english, if I issue an ``ls -l`` `(5 bytes without new line)` command and the `3rd byte` of the payload generated happens to be ``\x67`` (due to encryption it probably won't be ``\x20`` `-space character-` anyway), this `Principle` says that if I issue again ``ls -l``, the 3rd byte has a `1/512` probability of being ``\x67`` again.


Implementation Pitfalls
-----------------------

**DUH!** ::

	The "No-Duplicate Principle" generally applies to all Stream Ciphers.
	So, as I use a (homebrew) Stream Cipher,
	I got that principle covered too. Right?


**Right. But...** this is tricky to implement for the **whole protocol**. That is **from first payload generated** and for **every payload**.

And the tricky part is that if the payload is **not tagged in any way** it is difficult for the listener to determine whether the received data is addressed to him and **not try to decrypt all kinds of received data**.

Making the listener **identify** whether the decrypted data is gibberish (and rollback the key if it is) will need to provide a concise definition of **what gibberish is**. And doing even that (`dangerous high entropy approach`) will disable the sender from **sending gibberish intentionally**. Not bright idea at all. `Crypted shellcodes` **look like gibberish** but I can see reasons for sending such things...

.. note:: "Decrypting" data that is **not addressed to the listener** is a big problem if a Stream Cipher is used. It makes one of the keys to cycle `without notifying the other side`, `ultimately scraping` the rest of the connection.


And that is as the data doesn't get transmitted through a known connection. TLS application data seem random too, but it travels through a TCP connection that **knows how to handle them because of the handshake**.

*In a backdoor a handshake will generate `signatures`, as any hardcoded `byte-position pair`.


And using a legit protocol like TLS would hardcode the `Network Agnostic` design all together. Yet TLS can be used, if wrapped with ``covertutils`` functions, but making the only option is far from useful.

So you see. It is indeed tricky...



OTP me to the `End of Love`
---------------------------

So, as using a single byte signature is a big **NO-NO** what stands out?

What if we encrypt a string with a Rolling Key and append it to the message?

As the key is rolling the "`No-Duplicate Principle`" applies to the ciphertext of the string. But now the listener **knows what to search for**. Decrypting a certain portion of the payload will have to result to the original string. If it does not, then the received data is of no interest for the listener (the sender didn't sent this one), and the key can be rolled back.

This is a kind of one time password (`OTP`) for each payload originally sent from the sender.

This mechanism is furtherly described in the Securosophy_ post, under the `How Streams are implemented` heading.

.. _Securosophy : https://securosophy.com/2017/04/22/reinventing-the-wheel-for-the-last-time-the-covertutils-package/

Still, there is a possibility for a random data packet that have been received to have the same decrypted value with that string and this will mean that the channel will hang. That possibility is more that finding a `Shiny Pokemon in Silver`__, so it is handled (`how` is also explained in the `blog post` above).


.. _celebi : https://i.ytimg.com/vi/O7ZsJV71ji0/maxresdefault.jpg


__  celebi_


..
	.. figure:: images/orchestrator.png
		:alt: alternate text
		:align: center
