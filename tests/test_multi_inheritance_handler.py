import unittest
from covertutils.handlers import *
from covertutils.orchestration import SimpleOrchestrator
# from covertutils.Handlers.BaseHandler import BaseHandler

out_len = 100
in_len = 100



from covertutils.payloads import GenericStages


fdict = {
	'control' : GenericStages['shellprocess']['marshal'],
	'main' : GenericStages['shellprocess']['marshal'],
}


# http://stackoverflow.com/questions/34884567/python-multiple-inheritance-passing-arguments-to-constructors-using-super

def recv(  ) :
    return '1'


def send(  raw ) :
    return None

orch2 = SimpleOrchestrator("pass!", 4, out_len, in_len , reverse = True)

class MyHandler( FunctionDictHandler, InterrogatingHandler, ResponseOnlyHandler ) :


	def __init__( self, recv, send, orch, delay = None, function_dict = None ) :

		super(MyHandler, self).__init__( recv, send, orch, delay_between = delay, function_dict = fdict, fetch_stream = 'control' )

		# InterrogatingHandler.__init__( self, recv, send, orch, delay_between = delay,  function_dict = fdict, fetch_stream = 'control' )
		# FunctionDictHandler.__init__( self, recv, send, orch, function_dict = fdict )


	def onChunk( self, stream, message ) : pass
	def onMessage( self, stream, message ) : pass
	def onNotRecognised( self ) : pass



class test_MultiInheritance( unittest.TestCase ) :


    def test_implementation( self ) :
        # handler = MyHandler()
        handler = MyHandler(  recv = recv, send = send, orch = orch2,  )
