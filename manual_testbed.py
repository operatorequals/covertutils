from covertutils.handlers.impl import SimpleShellHandler, ExtendableShellHandler
from covertutils.handlers import FunctionDictHandler, BaseHandler, StageableHandler

from covertutils.orchestration import SimpleOrchestrator

from covertutils.shells import BaseShell
from covertutils.shells.impl import ExtendableShell

from os import urandom
from time import sleep
import re

out_length = 20
in_length = 20


orch1 = SimpleOrchestrator( "passphrase",
	2, out_length, in_length,
	# streams = ['main', 'shellcode', 'python']
	)


orch2 = SimpleOrchestrator( "passphrase",
	2, out_length, in_length,
	reverse = True,
	# streams = ['main', 'shellcode', 'python'],
	)

toAgent = []
toHandler = []

def dummy_receive1( ) :
	while not toAgent :
		sleep(0.01)
	# print( "Receiving" )
	return toAgent.pop(0)

def dummy_send1( raw ) :
	toHandler.append(raw)



def dummy_receive2( ) :
	while not toHandler :
		sleep(0.01)
	# print( "Receiving" )
	return toHandler.pop(0)

def dummy_send2( raw ) :
	toAgent.append(raw)


chunks_sent = 0
chunks_received = 0

agent = ExtendableShellHandler( dummy_receive1, dummy_send1, orch1 )



class MyHandler (BaseHandler) :

	def onMessage(self, stream, message) :
		# global chunks_sent
		# print( "Handler: Chunks Received: %d" % chunks_sent )
		chunks_sent = 0
		# print( message )
		pass
	def onChunk(self, stream, message) :
		# global chunks_sent
		# if chunks_sent == 0 :
		# 	print
		# chunks_sent += 1logname
		# print( "Handler: <Chunk>" )
		pass
	def onNotRecognised(self, stream, message) :
		# print( "Handler: <Unrecognised>"  )
		pass






handler = MyHandler( dummy_receive2, dummy_send2, orch2 )

# shell = ExtendableShell(handler, output = '/tmp/covertutils_out')
# shell = ExtendableShell(handler, output='/tmp/covertutils_session1')
shell = ExtendableShell(handler, output=True)

shell.start( False )
