from covertutils.orchestration import SimpleOrchestrator

orch_obj = SimpleOrchestrator(
        "Our passphrase can be anything! &^&%{}",
        out_length = 20,
        in_length = 20,
        )


import socket
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("127.0.0.1",1234))

def send( data ) :
        s.sendall( data )

def recv() :		# Return for every 20 bytes
        return s.recv(20)     # This will automatically block as socket.recv() is a blocking method


from covertutils.handlers import BaseHandler

class MyAgent_Handler( BaseHandler ) :
        """ This class tries hard to be self-explanatory """

        def __init__(self, recv, send, orch, **kw) :
                super( MyAgent_Handler, self ).__init__( recv, send, orch, **kw )
                print ( "[!] Agent with Orchestrator ID: '{}' started!".format( orch.getIdentity() ) )
                print()


        def onMessage( self, stream, message ) :
                print ( "[+] Message arrived!" )
                print ( "{} -> {}".format(stream, message) )
                print ("[>] Sending the received message in reverse order!")
                self.preferred_send( message[::-1] )    # Will respond with the reverse of what was received!

        def onChunk( self, stream, message ) :
                print ( "[+] Chunk arrived for stream '{}' !".format(stream) )
                if message :
                        print ("[*] Message assembled. onMessage() will be called next!")
                print()

        def onNotRecognised(self) :
                print ("[-] Got some Gibberish")
                print ("Initialized the Orchestrator with wrong passphrase?")
                print()

handler_obj = MyAgent_Handler(recv, send, orch_obj)

from time import sleep

while True : sleep(10)
