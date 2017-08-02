import cmd
import re

from covertutils.shells.subshells import SimpleSubShell

class ExampleSubShell ( SimpleSubShell ) :

	intro = """
This is an Example Shell. It has a custom prompt, and reverses all input before sending to the stage.
"""
	def __init__( self, stream, handler, queue_dict, base_shell, ignore_messages = set(['X']), prompt_templ = " ExampleSubShell Stream:[{stream}]==> ") :
		SimpleSubShell.__init__( self, stream, handler, queue_dict, base_shell, ignore_messages, prompt_templ )
		self.updatePrompt( )

	def default( self, line ) :
		command = line[::-1]
		print "Sending '%s' to the 'example' agent!" % command
		self.handler.preferred_send( command, self.stream )
