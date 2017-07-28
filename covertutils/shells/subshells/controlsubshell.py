import cmd
import re

from covertutils.shells.subshells import SimpleSubShell

from covertutils.payloads.generic.control import Commands as control_commands


class ControlSubShell ( SimpleSubShell ) :

	def __init__( self, stream, handler, queue_dict, base_shell, ignore_messages = set(['X']), prompt_templ = " (>{stream}<) |-> ") :
		SimpleSubShell.__init__( self, stream, handler, queue_dict, base_shell, ignore_messages, prompt_templ )
		self.updatePrompt( )

	def default( self, line ) :

		comm, args, line = self.parseline(line)
		try :
			command = control_commands[comm]
		except :
			print "No such control command!"
			return
		# print "Sending '%s' command" % command
		if command == control_commands['reset'] :
			print "Reseting handler"
			self.resetHandler()

		print "Sending '%s' control command!" % command
		self.handler.preferred_send( command, self.stream )


	def resetHandler( self ) :
		self.handler.reset()
