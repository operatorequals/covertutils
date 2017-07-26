from covertutils.handlers.impl import SimpleShellHandler
from covertutils.handlers import FunctionDictHandler, BaseHandler

from covertutils.orchestration import SimpleOrchestrator

from covertutils.shells import PrintShell

from os import urandom
from time import sleep
import re

out_length = 20
in_length = 20


orch1 = SimpleOrchestrator( "passphrase",
	2, out_length, in_length)

orch2 = SimpleOrchestrator( "passphrase",
	2, out_length, in_length,
	reverse = True)

toAgent = []
toHandler = []

def dummy_receive1( ) :
	while not toAgent :
		sleep(0.1)
	# print "Receiving"
	return toAgent.pop(0)

def dummy_send1( raw ) :
	toHandler.append(raw)



def dummy_receive2( ) :
	while not toHandler :
		sleep(0.1)
	# print "Receiving"
	return toHandler.pop(0)

def dummy_send2( raw ) :
	toAgent.append(raw)



agent = SimpleShellHandler( dummy_receive1, dummy_send1, orch1 )



class MyHandler (BaseHandler) :

	def onMessage(self, stream, message) :
		pass
	def onChunk(self, stream, message) :
		pass
	def onNotRecognised(self, stream, message) :
		pass


handler = MyHandler( dummy_receive2, dummy_send2, orch2 )

shell = PrintShell(handler)

shell.start()
