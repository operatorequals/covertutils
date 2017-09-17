
from covertutils.handlers.multi import MultiHandler

from covertutils.handlers import BufferingHandler


from covertutils.handlers.impl import SimpleShellHandler, ExtendableShellHandler
from covertutils.handlers import FunctionDictHandler, BaseHandler, StageableHandler

from covertutils.orchestration import SimpleOrchestrator

from os import urandom
from time import sleep


out_length = 20
in_length = 20


def create_wrappers() :

	passw = urandom(8).encode('hex')
	orch1 = SimpleOrchestrator( passw,
		2, out_length, in_length,
		# streams = ['main', 'shellcode', 'python']
		)


	orch2 = SimpleOrchestrator( passw,
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


	return {'recv' : [dummy_receive1, dummy_receive2], 'send' : [dummy_send1, dummy_send2], 'orch' : [orch1, orch2], 'orch_id' : [orch1.getIdentity(), orch2.getIdentity()] }

chunks_sent = 0
chunks_received = 0

wrappers1 = create_wrappers()
wrappers2 = create_wrappers()
wrappers3 = create_wrappers()

agent1 = ExtendableShellHandler( wrappers1['recv'][0], wrappers1['send'][0], wrappers1['orch'][0] )
agent2 = ExtendableShellHandler( wrappers2['recv'][0], wrappers2['send'][0], wrappers2['orch'][0] )
agent3 = ExtendableShellHandler( wrappers3['recv'][0], wrappers3['send'][0], wrappers3['orch'][0] )

class MyHandler (BaseHandler) :

	def onMessage(self, stream, message) :
		super(MyHandler, self).onMessage(stream, message)
		global chunks_sent
		print( "Handler: Chunks Received: %d" % chunks_sent )
		chunks_sent = 0
		# print( message )
		pass
	def onChunk(self, stream, message) :
		global chunks_sent
		# if chunks_sent == 0 :
			# print
		# print( "Handler: <Chunk>" )
		pass
	def onNotRecognised(self, stream, message) :
		# print( "Handler: <Unrecognised>"  )
		pass


# BufferizedHandler = BufferingHandler.bufferize_handler(MyHandler)



handler1 = MyHandler( wrappers1['recv'][1], wrappers1['send'][1], wrappers1['orch'][1] )
handler2 = MyHandler( wrappers2['recv'][1], wrappers2['send'][1], wrappers2['orch'][1] )
handler3 = MyHandler( wrappers3['recv'][1], wrappers3['send'][1], wrappers3['orch'][1] )




class MyMultiHandler (MultiHandler):

	def onMessage( self, stream, message ) :
		print stream, message

	def onChunk(self, stream, message) :
		# print "Got A chunk in MultiHandler"
		# print stream, message
		# global chunks_sent
		# if chunks_sent == 0 :
		# 	print
		# chunks_sent += 1logname
		# print( "Handler: <Chunk>" )
		pass

	def onNotRecognised(self, stream, message) :
		# print( "Handler: <Unrecognised>"  )
		pass





multi_handler = MyMultiHandler( [handler1, handler2, handler3] )

# import pdb; pdb.set_trace()

sleep(0.5)
# multi_handler.start()

# print "Ready!"

# handler.sendAdHoc("SI")
# handler.sendAdHoc("ID")

orch_id = wrappers1['orch_id'][1]

multi_handler.dispatch('%s:control' % orch_id, 'SI')
multi_handler.sendAll('SI')
# multi_handler.sendAll('ID')

# print "Printing streams"
# print multi_handler.getOrchestrator().getStreams()
# handler.sendAdHoc("ls")
# sleep(1)
# print multi_handler.get()

sleep(2)
multi_handler.sendAll('RST')
multi_handler.sendAll('ID')
sleep(2)
