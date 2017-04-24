# covertutils
A framework for Remote Code Execution Agent programming.

[![Documentation Status](https://readthedocs.org/projects/covertutils/badge/?version=latest)](http://covertutils.readthedocs.io/en/latest/?badge=latest) [![PyPI version](https://badge.fury.io/py/covertutils.svg)](https://pypi.python.org/pypi/covertutils)          [![GitHub version](https://badge.fury.io/gh/operatorequals%2Fcovertutils.svg)](https://github.com%2Foperatorequals%2Fcovertutils) [![Build Status](https://travis-ci.org/operatorequals/covertutils.svg?branch=master)](https://travis-ci.org/operatorequals/covertutils)

[Documentation Page](https://covertutils.readthedocs.io)

### What is it?
This python package automatically handles all communication channel options, like **encryption**, **chunking**, **steganography**, etc.

With all those set with a few lines of code, a programmer can spend time creating the *actual payloads*, *persistense mechanisms*, *shellcodes* and generally **more creative stuff!**!

The security programmers can stop *re-inventing the wheel* by implementing encryption mechanisms both agent-side and handler-side to spend their time to develop more versatile *agents*, and generally feature-full shells!

### Python?
Yes, python, and more specifically python 2.7 only, for the time being...


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
```
def onMessage( message, stream ) :
  if stream == 'shell' :
    os.system( message )
```

## Networking
Networking is not handled by `covertutils`, as python provides great built-in networking API (directly inherited from C). The only requirements for `covertutils` Handlers are **2 functions wrapping the raw data sending and receiving**.


Just pass a `send( raw )` and a `recv()` function to a `Handler` and you have a working *One-Time-Pad* encrypted, bandwidth aware, protocol independent, *password protected* channel.

# Further Examples:
Sample TCP/UDP Reverse Shells and TCP Bind Shell scripts can be found in `examples/` directory.


# Pull Requests?
Certainly! All pull requests that are tested and do not break the existing tests will be accepted!
Especially Pull Requests towards Python2/Python3 compatibility will be greatly appreciated!
