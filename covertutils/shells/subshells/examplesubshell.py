from covertutils.shells.subshells import SimpleSubShell

class ExampleSubShell ( SimpleSubShell ) :

	intro = """
This is an Example Shell. It has a custom prompt, and reverses all input before sending to the stage.
	"""
	def __init__( self, stream, handler, queue_dict, base_shell, ignore_messages = set(['X']), prompt_templ = " ExampleSubShell Stream:[{stream}]==> ") :
		SimpleSubShell.__init__( self, stream, handler, queue_dict, base_shell, ignore_messages, prompt_templ )
		"""A method that uses the `prompt_templ` argument
		to reformat the prompt
		(in case the `format()` {tags} have changed)"""
		self.updatePrompt()

	def default( self, line ) :
		command = line[::-1]	# Reversing the user input string
		print "Sending '%s' to the 'example' agent!" % command
		self.handler.preferred_send( command, self.stream )
