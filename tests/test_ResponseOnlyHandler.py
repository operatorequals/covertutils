import unittest

from covertutils.handlers import BaseHandler, ResponseOnlyHandler
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
		sleep(0.001)
	return recvd1.pop(0)

def dummy_send1( raw ) :
	recvd1.append( raw )


recvd2 = []
def dummy_receive2( ) :
	while not recvd2 :
		sleep(0.001)
	return recvd2.pop(0)

def dummy_send2( raw ) :
	recvd2.append( raw )

testable = False


class CustomRespOnlyHandler( ResponseOnlyHandler ) :

	def onChunk( self, stream, message ) :  pass
	def onNotRecognised( self ) :  pass


class CustomTestHandler( BaseHandler ) :

	def onChunk( self, stream, message ) :  pass
	def onNotRecognised( self ) :  pass
	def onMessage( self, stream, message ) :
		global testable
		testable = message


class Test_ResponseOnlyHandler( unittest.TestCase ) :


	def setUp( self ) :
		self.p_handler = CustomRespOnlyHandler( recv = dummy_receive1, send = dummy_send2, orchestrator = orch2, )
		self.test_handler = CustomTestHandler( dummy_receive2, dummy_send1, orch1 )



	def test_functionality( self, n = 100, l = 10 ) :

		global testable
		for i in  range(n) :
			message = urandom(l)
			self.p_handler.queueSend( message, 'control' )
			self.assertTrue( testable == False )

			self.test_handler.sendAdHoc( ResponseOnlyHandler.Defaults['request_data'] )

			while testable == False :
				sleep(0.01)

			self.assertTrue( testable == message )
			testable = False


	def test_multi_chunk( self, n = 10, l = 200 ) :

		global testable
		for i in  range(n) :
			message1 = urandom(l)
			message2 = urandom(l)
			self.p_handler.queueSend( message1 )
			self.p_handler.queueSend( message2, 'control' )
			self.assertTrue( testable == False )

			while testable == False :
				# print testable
				self.test_handler.sendAdHoc( ResponseOnlyHandler.Defaults['request_data'], 'control' )
				sleep(0.01)


			self.assertTrue( testable == message1 )
			# print "Passed 1"
			testable = False

			while testable == False :
				self.test_handler.sendAdHoc( ResponseOnlyHandler.Defaults['request_data'] )
				sleep(0.01)
			while testable == False :
				sleep(0.01)

			self.assertTrue( testable == message2 )
			testable = False
			# print "Passed 2"
