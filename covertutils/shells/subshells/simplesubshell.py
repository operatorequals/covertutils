import cmd

from threading import Thread



def _print( str_, instance ) :
	print str_


class SimpleSubShell ( cmd.Cmd ) :


	message_function = _print

	def __init__( self, stream, handler, queue_dict, base_shell, ignore_messages = set(['X']), prompt_templ = "[{stream}]> ") :

		cmd.Cmd.__init__(self)

		self.stream = stream
		self.handler = handler
		self.queue_dict = queue_dict
		self.ignore_messages = ignore_messages
		self.message_function = _print
		self.prompt_templ = prompt_templ
		self.updatePrompt()
		self.base_shell = base_shell

		self.work_thr = Thread( target = self.__working_daemon )
		self.work_thr.daemon = True
		self.work_thr.start()



	def __working_daemon( self ) :

		while True :
			self.queue_dict['condition'].acquire()
			if self.queue_dict['messages'].empty() :
				# print "Waiting for Condition"
				self.queue_dict['condition'].wait()
				# print "Condition met"
			message = self.queue_dict['messages'].get()
			# print "Message acquired"
			if message not in self.ignore_messages :
				self.message_function( message, self )
				# print "Message processed"
				self.queue_dict['messages'].task_done()
			# print message not in self.ignore_messages
			self.queue_dict['condition'].release()
			# print "Condition released"


	def precmd( self, line ) :
		# print "%s" % line
		if not line : return line
		line_ = line.strip()
		# print line_.startswith( self.base_shell.stream_preamp_char )
		# print line[1:]
		if line_.startswith( self.base_shell.stream_preamp_char ) :
			try :
				self.base_shell.default(line_)
				return ''		# don't run default() in this case
			except :
				self.base_shell.streamCharacterHelp()
				return line
		return line


	def default( self, line ) :
		# print "Triggered %s for '%s'" % (self.stream, line)
		self.handler.preferred_send( line, self.stream )



	def updatePrompt( self ) :
		self.prompt = self.prompt_templ.format( stream = self.stream  )


	def start( self ) :
		try :
			self.cmdloop()
		except KeyboardInterrupt :
			print
			pass

	def emptyline( self ) :
		return
