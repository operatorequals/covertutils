from covertutils.handlers import BufferingHandler

from threading import Thread

from time import sleep

class SimpleBridge :
	"""
The Bridge class is used to pass messages between 2 Handler objects. It can be used to bridge an Agent and a Handler using a third host.
	"""

	def __init__( self, lhandler, rhandler ) :

		if not( isinstance(lhandler, BufferingHandler) and isinstance(rhandler, BufferingHandler) ) :
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
			# print "Started loop"
			lcondition.acquire()
			if lhandler.empty() :
				lcondition.wait()

			# print "Acquired condition"
			stream, message = lhandler.get()
			# print "Sending"
			rhandler.preferred_send( message, stream )
			lcondition.release()
			# print "Leaving loop"
			sleep(0.01)
