from covertutils.handlers.impl import SimpleShellHandler
from covertutils.handlers import FunctionDictHandler, BaseHandler

from covertutils.orchestration import SimpleOrchestrator

from covertutils.shells import PrintShell, BaseShell

from covertutils.payloads import CommonStages, LinuxStages

from os import urandom
from time import sleep
import re

out_length = 20
in_length = 20


orch1 = SimpleOrchestrator( "passphrase",
	2, out_length, in_length,
	# streams = ['main', 'shellcode']
	)


orch2 = SimpleOrchestrator( "passphrase",
	2, out_length, in_length,
	reverse = True,
	streams = ['main', 'shellcode'],
	)

toAgent = []
toHandler = []

def dummy_receive1( ) :
	while not toAgent :
		sleep(0.01)
	# print "Receiving"
	return toAgent.pop(0)

def dummy_send1( raw ) :
	toHandler.append(raw)



def dummy_receive2( ) :
	while not toHandler :
		sleep(0.01)
	# print "Receiving"
	return toHandler.pop(0)

def dummy_send2( raw ) :
	toAgent.append(raw)


chunks_sent = 0
chunks_received = 0

class AgentHandler( FunctionDictHandler ) :

	def onMessage(self, stream, message) :
		global chunks_sent
		stream, ret = super( AgentHandler, self).onMessage( stream, message )
		self.preferred_send(ret)
		print "Agent: Chunks Received: %d" % chunks_sent
		chunks_sent = 0

	def onChunk(self, stream, message) :
		global chunks_sent
		chunks_sent += 1
		pass

	def onNotRecognised(self) :
		pass





f_dict = {
	# 'control' : CommonStages['shell']['function'],
	# 'main' : CommonStages['sysinfo']['function'],
	# 'shellcode' : LinuxStages['shellcode']['function'] ,

CommonStages['shell_proc']
}

# agent = SimpleShellHandler( dummy_receive1, dummy_send1, orch1)

agent = AgentHandler( dummy_receive1, dummy_send1, orch1, function_dict = f_dict )



class MyHandler (BaseHandler) :

	def onMessage(self, stream, message) :
		global chunks_sent
		print "Handler: Chunks Received: %d" % chunks_sent
		chunks_sent = 0
		# print message
		pass
	def onChunk(self, stream, message) :
		global chunks_sent
		if chunks_sent == 0 :
			print
		chunks_sent += 1
		# print "Handler: <Chunk>"
		pass
	def onNotRecognised(self, stream, message) :
		# print "Handler: <Unrecognised>"
		pass




# class CustomShell( BaseShell ) :




handler = MyHandler( dummy_receive2, dummy_send2, orch2 )

shell = PrintShell(handler)

shell.start()
