import cmd
import re

from covertutils.shells.subshells import SimpleSubShell

# cmd.IDENTCHARS += ' '
class PythonAPISubShell ( SimpleSubShell ) :

	# identchars = SimpleSubShell.identchars + ' '
	indentation = False
	intented_prompt = '...'
	unintented_prompt = '>>>'
	special_comm_char = '@'
	append_comm_char = '+'


	def __init__( self, stream, handler, queue_dict, base_shell, ignore_messages = set(['X']), prompt_templ = "[{stream}] {intent_str} ") :
		# print ShellcodeSubShell
		SimpleSubShell.__init__( self, stream, handler, queue_dict, base_shell, ignore_messages, prompt_templ )
		self.indentation = False
		self.python_buffer = ''
		self.file_buffer = ''
		# self.use_rawinput = False
		self.updatePrompt( )
		self.special_commands = {
			'storage' : self.showStorage,
			'pyload' : self.loadFile,
			'show' : self.showBuffer,
			'clear' : self.clearBuffer,
			'send' : self.sendFileBuffer,
			'append' : self.appendFileBuffer,
		}



	def parseline(self, line) :
		return None, None, line		# Do not do any autmatic parsing. indentation gets fucked up

	def sendPythonBuffer( self, buffer_ = None ) :
		if not buffer_ :
			buffer_ = self.python_buffer
		if not buffer_ :
			print "Nothing to send"
			return
		try:
			compile(buffer_, "<local>", "exec")
		except Exception as e:
			print "\t==== Local Syntax Check ===="
			print "Problem: %s" % e
			print "\tChecked code:"
			print buffer_
			buffer_ = ''
			print "\t<Nothing Transmitted>"
			return
		self.handler.preferred_send( buffer_, self.stream )
		self.python_buffer = ''
		self.file_buffer = ''


	def default( self, line ) :

		if len(line) == 0 :
			self.indentation = False
			if self.python_buffer :
				self.sendPythonBuffer()
			return

		if line[0] == self.special_comm_char :
			if not self.indentation :
				self.specialCommand(line[1:])
				return

		line = line.rstrip()
		self.python_buffer += line+'\n'
		if self.indentation or line[-1] == ':'	: # indentation pending
			# print line[-1] == ':'
			self.indentation = True

		if not self.indentation :
			self.sendPythonBuffer()
		return


	def postcmd( self, stop, line ) :
		self.updatePrompt( )


	def updatePrompt( self ) :
		if self.indentation :
			self.prompt = self.prompt_templ.format( stream = self.stream,  intent_str = self.intented_prompt  )
		else :
			self.prompt = self.prompt_templ.format( stream = self.stream,  intent_str = self.unintented_prompt  )


	def emptyline( self ) :
		self.indentation = False
		self.default( '' )




#	=====================	Special Commands	=====================
	def clearBuffer( self, line ) :
		self.python_buffer = ''
		print "Buffer cleared!"

	def showStorage( self, line ) :
		print
		self.onecmd("import pprint; pprint.pprint (storage)")

	def loadFile( self, line ) :
		self.clearBuffer('')
		filename = line.strip().split()[0]
		if not filename :
			print "No filename specified!"
			return
		try :
			with open(filename, 'r') as f :
				self.file_buffer += f.read()
			print "File '%s' loaded!" % filename
		except IOError :
			print "File '%s' doesn't exist!" % filename

	def showBuffer( self, line ) :
		if not self.file_buffer :
			print "Buffer is empty"
			return
		print self.ruler*20
		print self.file_buffer
		print self.ruler*20

	def appendFileBuffer( self, line ) :
		self.file_buffer += line + '\n'

	def sendFileBuffer( self, line ) :
		self.sendPythonBuffer( self.file_buffer )


	def specialCommand( self, line ) :
		# line = line.strip()
		if not line :
			print "No special command specified!"

		toks = line.split(None, 1)
		if not toks :
			print "Available special commands:"
			print '\n'.join(['\t'+self.special_comm_char+comm for comm in self.special_commands.keys()])
			return
		comm = toks[0]
		arg_line = ''
		if len(toks) > 1 :
 			arg_line = toks[1]

		try :
			self.special_commands[comm](arg_line)
		except KeyError:
			print "Special command '%s' not found" % comm
