import unittest

from covertutils.handlers import BaseHandler, ResponseOnlyHandler, InterrogatingHandler
from covertutils.orchestration import SimpleOrchestrator

from os import urandom
from time import sleep
from hashlib import sha512
import re


out_length = 50
in_length = 40

passp = "passphrase"

orch1 = SimpleOrchestrator( passp,
    2, out_length, in_length,
    cycling_algorithm = sha512)

orch2 = SimpleOrchestrator( passp,
    2, out_length, in_length,
    cycling_algorithm = sha512, reverse = True)


recvd1 = []
def dummy_receive1( ) :
    while not recvd1 :
        sleep(0.0001)
    return recvd1.pop(0)

def dummy_send1( raw ) :
    recvd1.append( raw )


recvd2 = []
def dummy_receive2( ) :
    while not recvd2 :
        sleep(0.0001)
    return recvd2.pop(0)

def dummy_send2( raw ) :
    recvd2.append( raw )

testable = False


class CustomInterrogatingHandler( InterrogatingHandler ) :

    def onChunk( self, stream, message ) :  pass
    def onNotRecognised( self ) :  pass

    def onMessage( self, stream, message ) :
        global testable
        testable = message


class CustomRespOnlyHandler( ResponseOnlyHandler ) :

    def onChunk( self, stream, message ) :  pass
    def onNotRecognised( self ) :  pass




class Test_InterrogatingHandler( unittest.TestCase ) :


    def setUp( self ) :
        self.p_handler = CustomInterrogatingHandler( dummy_receive1, dummy_send2, orch2 , req_data = 'X', delay_between = (0, 0.01), fetch_stream = 'control' )
        self.test_handler = CustomRespOnlyHandler( dummy_receive2, dummy_send1, orch1 , req_data = 'X' )



    def test_functionality( self, n = 10, l = 10 ) :

        global testable
        for i in  range(n) :
            message = urandom(l)
            self.test_handler.queueSend( message, 'control' )

            sleep(0.03)
            self.assertTrue( testable == message )
            testable = False
