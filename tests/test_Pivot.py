import unittest

from covertutils.handlers import BaseHandler, BufferingHandler
from covertutils.orchestration import SimpleOrchestrator

from covertutils.bridges import SimpleBridge

from os import urandom
from time import sleep
from hashlib import sha512
import re



out_length = 50
in_length = 40

passp1 = "passphrase"
passp2 = "passphrase2"

orch1 = SimpleOrchestrator( passp1,
	2, out_length, in_length,
	cycling_algorithm = sha512)

orch2 = SimpleOrchestrator( passp1,
	2, out_length, in_length,
	cycling_algorithm = sha512, reverse = True)

orch3 = SimpleOrchestrator( passp2,
	2, out_length, in_length,
	cycling_algorithm = sha512)

orch4 = SimpleOrchestrator( passp2,
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


recvd3 = []
def dummy_receive3( ) :
	while not recvd3 :
		sleep(0.0001)
	return recvd3.pop(0)

def dummy_send3( raw ) :
	recvd3.append( raw )


recvd4 = []
def dummy_receive4( ) :
	while not recvd4 :
		sleep(0.0001)
	return recvd4.pop(0)

def dummy_send4( raw ) :
	recvd4.append( raw )

end = False
start = False


class EndHandler( BaseHandler ) :

	def onChunk( self, stream, message ) :  pass
	def onNotRecognised( self ) :  pass
	def onMessage( self, stream, message ) :
		global end
		end = message
		# print( "%s : (%s: %s)" % ( "End", stream, message ) )
		self.sendAdHoc( message, stream )			# echo the input back


class StartHandler( BaseHandler ) :

	def onChunk( self, stream, message ) :  pass
	def onNotRecognised( self ) :  pass
	def onMessage( self, stream, message ) :
		global start
		start = message
		# print( "%s : (%s: %s)" % ( "Start", stream, message ) )


class IntermediateHandler( BufferingHandler ) :

	def onChunk( self, stream, message ) :	pass
	def onNotRecognised( self ) :	pass
	def onMessage( self, stream, message ) :
		# print( "BufferingHandler : (%s: %s)" % ( stream, message ) )
		super( IntermediateHandler, self ).onMessage( stream, message )


class Test_SimpleBridge( unittest.TestCase ) :

	def setUp( self ) :

		self.endHandler1 = EndHandler( recv = dummy_receive1, send = dummy_send2, orchestrator = orch1 )
		self.bridgeHandler1 = IntermediateHandler( recv = dummy_receive2, send = dummy_send1, orchestrator = orch2 )
		self.bridgeHandler2 = IntermediateHandler( recv = dummy_receive3, send = dummy_send4, orchestrator = orch3 )
		self.startHandler = StartHandler( recv = dummy_receive4, send = dummy_send3, orchestrator = orch4 )

		self.bridge = SimpleBridge( self.bridgeHandler1, self.bridgeHandler2 )


	def test_one_way( self ) :
		data = "A"*100
		global start
		self.startHandler.sendAdHoc( data )

		while not end :
			sleep(0.01)
		# print( start, end )
		start = False
		self.assertTrue( data == end )

	def test_two_way( self ) :
		data = "A"*1000
		global end
		self.startHandler.sendAdHoc( data )

		while not start :
			sleep(0.01)
		# print( start, end )
		end = False
		self.assertTrue( data == start )

	def test_exception( self ) :
		try :
			bridge = SimpleBridge( None, self.startHandler  )
			test = False
		except TypeError :
			test = True

		self.assertTrue( test )
