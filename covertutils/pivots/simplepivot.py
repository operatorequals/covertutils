from covertutils.handlers import BufferingHandler

from threading import Thread

from time import sleep

class SimplePivot :
	"""
The Pivot class is used to pass messages between 2 Handler objects. It can be used to bridge an Agent and a Handler using a third host.
	"""

	def __init__( lhandler, rhandler ) :

		if type(lhandler) != BufferingHandler or type(rhandler) != BufferingHandler :
			raise TypeError( "Argument is not of type 'BufferingHandler'" )

		self.lcondition = lhandler.getCondition()
		self.rcondition = rhandler.getCondition()


		self.l2r_thread = Thread( target = self.__intercommunication, args = ( lhandler, rhandler, self.lcondition ) )
		self.r2l_thread = Thread( target = self.__intercommunication, args = ( rhandler, lhandler, self.rcondition ) )

		self.r2l_thread.daemon = True
		self.l2r_thread.daemon = True

		self.r2l_thread.start()
		self.l2r_thread.start()


	def __intercommunication( self, lhandler, rhandler, lcondition ) :

		while True :

			lcondition.acquire()
			if lhandler.count() == 0 :
				lcondition.wait()

			stream, message = lhandler.pop()
			rhandler.preferred_send( message, stream )
			lcondition.release()
			sleep(0.1)
