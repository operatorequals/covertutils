from covertutils.handlers import BufferingHandler

from threading import Thread

from time import sleep

class SimplePivot :


	def __init__( lhandler, rhandler ) :

		if type(lhandler) != BufferingHandler or type(rhandler) != BufferingHandler :
			raise TypeError( "Argument is not of type BufferingHandler" )

		self.l2r_thread = Thread( target = self.__intercommunication, args = ( lhandler, rhandler ) )
		self.r2l_thread = Thread( target = self.__intercommunication, args = ( rhandler, lhandler ) )

		self.r2l_thread.daemon = True
		self.l2r_thread.daemon = True

		self.r2l_thread.start()
		self.l2r_thread.start()


	def __intercommunication( self, lhandler, rhandler ) :

		while True :
			sleep( 0.1 )
			try :
				stream, message = lhandler.pop()
				rhandler.preferred_send( message, stream )
			except :
				pass
