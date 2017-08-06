from covertutils.orchestration import SimpleOrchestrator

orch_obj = SimpleOrchestrator(
        "Our passphrase can be anything! &^&%{}",
        out_length = 20,
        in_length = 20,
        reverse = True, # <-------
        )

import socket

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # To make the port immediately available after killing - gimmick
s.bind( ("0.0.0.0", 1234) )
s.listen(5)

client, client_addr = s.accept()


def recv () :           # Create wrappers for networking
        return client.recv( 20 )

def send( raw ) :               # Create wrappers for networking
        return client.sendall( raw )


from covertutils.handlers import BaseHandler

class MyHandler_Handler( BaseHandler ) :
        """ This class tries hard to be self-explanatory """

        def __init__(self, recv, send, orch, **kw) :
                super( MyHandler_Handler, self ).__init__( recv, send, orch, **kw )
                print ( "[!] Handler with Orchestrator ID: '{}' started!".format( orch.getIdentity() ) )
                print()


        def onMessage( self, stream, message ) :
                print ( "[+] Message arrived!" )
                print ( "{} -> {}".format(stream, message) )
                print ( "[<] Original Message {}".format(message[::-1]) ) # <-------

        def onChunk( self, stream, message ) :
                print ( "[+] Chunk arrived for stream '{}' !".format(stream) )
                if message :
                        print ("[*] Message assembled. onMessage() will be called next!")
                print()

        def onNotRecognised(self) :
                print ("[-] Got some Gibberish")
                print ("Initialized the Orchestrator with wrong passphrase?")
                print()


handler_obj = MyHandler_Handler(recv, send, orch_obj)

try: input = raw_input  # Python 2/3 nonsense
except NameError: pass  # (fuck my life)

while True :
        inp = input("~~~> ")
        if inp :
                handler_obj.preferred_send( inp )
