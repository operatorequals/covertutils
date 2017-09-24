import cmd
import sys
import argparse
import threading

from covertutils.handlers.multi import MultiHandler
#
#	The idea is to pass a list of handlers to start with, and create a MultiHandler object from this list.
#
#	The initial arguments for this should be a list of Shells. From shells, the handlers will be retrieved and from there, the MultiHandler object will be created
#
try:
	raw_input          # Python 2
except NameError:
	raw_input = input  # Python 3


class CLIArgumentParser( argparse.ArgumentParser ) :
	def exit(self, ex_code = 1, message = "Unrecognised") :
		# print message
		# print '[!] [EXIT] - ', ex_code, message
		return

	def error(self, message) : print (message)


class MultiShell( cmd.Cmd ) :

	def __init__( self, shells = [], output = None ) :
		cmd.Cmd.__init__(self)
		self.shells = {}
		for shell in shells :
			self.__add_handler_shell( shell )

		self.prompt = 'covertpreter> '


	def __add_handler_shell( self, shell ) :
		self.shells[shell.handler.getOrchestrator().getIdentity()] = shell


	def list_sessions( self, verbose = False ) :

		handlers = [shell.handler for shell in self.shells.values()]
		to_show = []
		for orch_id, shell in self.shells.iteritems() :
			# print shell.sysinfo
			try :
				sysinfo = shell.sysinfo
				sysinfo = ' - '.join([sysinfo[i] for i in (0,4,3,8)])	# hostname, distro, locale, user
			except Exception as e:
				# print e
				sysinfo = None		# Could dispatch selectively a 'SI' command
			handler = shell.handler
			if verbose :
				streams = handler.getOrchestrator().getStreams()
			else :
				streams = []
			to_show.append( {'row' : (orch_id, handler.__class__) , 'streams' : streams, 'info' : sysinfo } )

		print ("\tCurrent Sessions:")
		for i, sess_dict in enumerate(to_show) :
			# print  row
			row = sess_dict['row']
			streams = sess_dict['streams']
			num_row = "%d) {:16} - {}" % (i)
			print ( num_row.format(*row) )
			if sess_dict['info'] :
				print sess_dict['info']
			else :
				print "System Info: N/A"
			for stream in streams :
				print ("\t-> {}".format(stream))
			print ('\n')


	def default(self, line) :
		if not line :
			return

		arg_parser = CLIArgumentParser(prog = "\n%s" % self.prompt)
		arg_parser.add_argument("SESSIONS", nargs = '*', help = 'The SESSIONS IDs that the MESSAGE must be sent to. If not provided, it defaults to ALL SESSIONS', default = None)
		arg_parser.add_argument("STREAM", type = str, help = 'The STREAM to send the MESSAGE. If a SESSION does not support the provided STREAM, it will be omitted')
		arg_parser.add_argument("MESSAGE", type = str, default = None, help = "The MESSAGE to send to the selected SESSIONS")

		try :
			args = arg_parser.parse_args( line.split() )
		except Exception as e :
			print e
			return
		if args.MESSAGE == None :
			# print arg_parser.print_help()
			return
		# print args
		if not args.SESSIONS :
			print "No sessions selected, ALL sessions will be commanded" # Warning
			# [y/n] thing
			resp = raw_input("Are you sure? [y/N]: ")
			if resp.lower() != 'y' :
				return
			else :
				args.SESSIONS = self.shells.keys()

		for session_id in args.SESSIONS :
			if session_id in self.shells.keys() :
				shell = self.shells[session_id]
				command = "{stream_char}{stream} {message}".format(
								stream_char = shell.stream_preamp_char,
								stream = args.STREAM,
								message = args.MESSAGE,
							)
				print ( "'%s' -> <%s>" % (command, session_id) )
				shell.onecmd( command )


	def do_session( self, line ) :
		arg_parser = CLIArgumentParser(prog = "session")
		arg_parser.add_argument("-i", "--session_num", help = "Jumps to the shell designated by the SESSION_NUM", type = int, required = False)
		arg_parser.add_argument("-s", "--session_id", help = "Jumps to the shell designated by the SESSIONS_ID", type = str, required = False)
		arg_parser.add_argument("-l", "--list", help = "Lists all current Session Shells", action = 'store_true' )
		arg_parser.add_argument("-v", help = "Verbose output of '-l'", action = 'store_true' )
		try :
			args = arg_parser.parse_args( line.split() )
		except Exception as e :
			print e
			return
		# print args
		if args.list :
				return self.list_sessions( args.v )
		try :
			i = args.session_num
			# print list(self.shells)[i]
			shell = self.shells.values()[i]
			return shell.start(False)
		except Exception as e:
			# print e
			pass

		if args.session_id in self.shells.keys() :
			shell = self.shells[args.session_id]
			return shell.start(False)


	def do_handler( self, line ) :

		arg_parser = CLIArgumentParser(prog='handler')
		subparsers = arg_parser.add_subparsers(help='command for the handler', dest="command")
		parser_add = subparsers.add_parser('add', help='Add a Handler in a new Thread and start a session')
		parser_add.add_argument("SCRIPT", help = "The file that contains the Handler in Python 'covertutils' code", type = str)
		parser_add.add_argument("ARGUMENTS", help = "The arguments passed to the Python 'covertutils' handler script", type = str, default = '', nargs = '*')
		parser_add.add_argument("--shell", '-s', help = "The argument in the Python code that contains the 'covertutils.shell.baseshell.BaseShell' implementation",
									type = str, default = 'shell')
		parser_del = subparsers.add_parser('del', help='Delete a Handler')
		parser_del.add_argument("SESSION_ID", help = "The ID of the SESSION to purge", type = str)
		parser_del.add_argument("--kill", '-k', help = "Send 'KILL' command to the corresponding Agent [TODO]", action = 'store_true', default = False)

		args = arg_parser.parse_args(line.split())
		# print args
		if args.command == 'add' :
			if args.SCRIPT == None :
				print arg_parser.print_help()
				return
			filename = args.SCRIPT
			arguments = args.ARGUMENTS
			shell_var = args.shell
			mount_thread = threading.Thread( target = self.mount_new_handler, args = ( filename, arguments, shell_var ) )
			mount_thread.daemon = True
			mount_thread.start()
		elif args.command == 'del' :
			if args.SESSION_ID == None :
				print arg_parser.print_help()
				return
			self.unmount_handler(args.SESSION_ID, args.kill)


	def unmount_handler( self, orch_id, kill = False ) :
		if orch_id in self.shells.keys() :
			if kill :
				self.shells[orch_id].onecmd("!control kill")
			self.shells[orch_id].handler.stop()
			# self.shells[orch_id].handler.receive_function = None
			del self.shells[orch_id]


	def mount_new_handler( self, filename, arguments, shell_var = 'shell' ) :	#  handler add examples/tcp_reverse_handler.py 8080 Pa55phra531
		variables = ['handler_filaneme.py'] + arguments
		sys.argv = variables
		print variables
		with open(filename, 'r') as handler_codefile :
			handler_code = handler_codefile.read()
			# namespace_dict = locals()
			namespace_dict = {}
			handler_code = handler_code.replace("%s.start()" % shell_var, 'pass')	# Replace the blocking command of the shell
			# exec( handler_code )
			exec( handler_code, namespace_dict )
			print namespace_dict[shell_var]
			self.__add_handler_shell( namespace_dict[shell_var] )
			print "Added Session!"


	def emptyline( self ) :	return
	def do_EOF( self, *args ) : return

	def do_exit( self, *args ) : return self.do_q( *args )
	def do_quit( self, *args ) : return self.do_q( *args )
	def do_q( self, *args ) : return self.quitPrompt()

	def quitPrompt( self, *args ) :
		# print( args )
		exit_input = raw_input("[!]\tQuit shell? [y/N] ")
		if exit_input.lower() == 'y' :
			print( "Aborted by the user..." )
			# sys.exit(0)
			return True
		return False

	def start( self, warn = True ) :
		# try :
		while True :
			ret = None
			try :
				ret = self.cmdloop()
				# if ret :
				break
			except KeyboardInterrupt :
				print ("\n[!] For exiting use [q|quit|exit]")
