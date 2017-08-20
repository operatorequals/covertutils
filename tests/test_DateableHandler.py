import unittest

from covertutils.handlers import DateableHandler
from covertutils.orchestration import SimpleOrchestrator

import datetime
from time import sleep
from pprint import pprint

out_length = 4
in_length = 4


orch1 = SimpleOrchestrator( "passphrase",
	2, out_length, in_length,
	# cycling_algorithm = sha512
	)

chunks = []
def dummy_receive( ) :
	while not chunks :
		sleep(0.1)
	# print "Receiving"
	return chunks.pop(0)


testable = None

def dummy_send( raw ) :
	global testable
	# print "sending!"
	stream, message = orch1.depositChunk( raw )
	if message :
		testable = message


class MyTestHandler(DateableHandler) :

	def onMessage(self, stream, message) : pass
	def onChunk(self, stream, message) : pass
	def onNotRecognised(self, stream, message) : pass


class Test_DateableHandler( unittest.TestCase ) :


	def setUp(self) :
		self.handler = MyTestHandler( dummy_receive, dummy_send, orch1, workinghours = ( (8,30), (16,30) ) )
		pprint( self.handler.dates )


	def testHoliday(self) :
		ny_Eve = datetime.datetime(2017, 1,1, 9, 10)
		print( ny_Eve )
		self.assertTrue( self.handler.mustNotRespond( ny_Eve ) )

		christmas = datetime.datetime(2017, 12, 25, 9, 10)
		print( christmas )
		self.assertTrue( self.handler.mustNotRespond( christmas ) )

		anyday = datetime.datetime(2017, 8, 7, 9, 10)
		self.assertTrue( not self.handler.mustNotRespond( anyday ) )


	# def testEaster(self) :
	#
	# 	easter = calc_easter(datetime.datetime.now().year)
	#
	# 	hols = [easter.days-1, easter.days-2, easter.days, easter.days+1, easter.days+2]
	# 	no_hols = [easter.days-3, easter.days-4, easter.days+4, easter.days+3, easter.days+5]
	#
	# 	# for hol in hols :
	# 	# 	d = calc_easter(datetime.datetime.now().year)
	# 	# 	d.day = hol

	def testWorkingHours(self) :

		anyday = datetime.datetime(2017, 5,1, 7, 10)
		print( anyday )
		self.assertTrue( self.handler.mustNotRespond( anyday ) )

		anyday = datetime.datetime(2017, 5,1, 20, 10)
		print( anyday )
		self.assertTrue( self.handler.mustNotRespond( anyday ) )

		anyday = datetime.datetime(2017, 5,1, 13, 10)	# Not a weekend
		print( anyday )
		self.assertTrue( not self.handler.mustNotRespond( anyday ) )
