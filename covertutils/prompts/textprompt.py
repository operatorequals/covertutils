import cmd
from covertutils.handlers import BaseHandler
import covertutils


class TextPrompt( cmd.Cmd ) :

	modifier_char = '!'
	def __init__( self, orchestrator, handler, prompt = "(%s v%s)[{0}]> " % ( covertutils.__name__, covertutils.__version__ ) ) :

		cmd.Cmd.__init__(self)

		self.handler = handler
		self.prompt_templ = prompt
		self.orchestrator = orchestrator
		self.current_stream = self.orchestrator.getDefaultStream()
		self.__updatePrompt()


	def __updatePrompt( self ) :
		self.prompt = self.prompt_templ.format( self.current_stream )


	def availableStreams(self) :
		return self.orchestrator.getStreams()


	def default( self, line ) :
		if not line.startswith( self.modifier_char ) :
			self.handler.sendAdHoc( line, self.current_stream )		# all messages go to the default stream
			return
		line = line[1:]
		if line in self.availableStreams() :
			self.current_stream = line
		self.__updatePrompt()

	def emptyline( self ) :
		return
