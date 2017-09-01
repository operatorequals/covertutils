import cmd
from covertutils.handlers import BaseHandler
import covertutils

class TextPrompt( cmd.Cmd ) :

	def __init__( self, handler, prompt = "(%s v%s) >" % ( covertutils.__name__, covertutils.__version__ ) ) :

		super( TextPrompt, self ).__init__( self )
		self.handler = handler
		self.prompt = prompt


	def default( self, line ) :
		self.handler.preferred_send( line )		# all messages go to the default stream


	def emptyline( self ) :
		return
