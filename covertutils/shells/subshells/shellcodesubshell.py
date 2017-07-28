import cmd
import re

from covertutils.shells.subshells import SimpleSubShell


def format_shellcode( unformatted ) :

	ready = unformatted

	ready = ready.split('=')[-1]	# in case shellcode[] = 'blah...'
	ready = ready.strip()
	ready = ready.replace('x','')
	ready = ready.replace('\n','')

	#	taken from https://stackoverflow.com/questions/1007481/how-do-i-replace-whitespaces-with-underscore-and-vice-versa
	# Remove all non-word characters (everything except numbers and letters)
	ready = re.sub(r"[^\w\s]", '', ready)
	# Replace all runs of whitespace with a single dash
	ready = re.sub(r"\s+", '-', ready)

	ready = ready.strip()	# strip after removing things
	ready = ready.decode('hex')	# make it binary
	return ready


def show( mixed_shellcode ) :

	print "Pasted lines:"
	print mixed_shellcode
	print
	try :
		pure_shellcode = format_shellcode( mixed_shellcode )
		print "Length of %d bytes" % len(pure_shellcode)
		print
		print "Shellcode in HEX :"
		print pure_shellcode.encode('hex')
		print
		print "Shellcode in BINARY :"
		print pure_shellcode

	except TypeError:
		print "Shellcode buffer could not be formatted"
		print "Pasted half a line?"



class ShellcodeSubShell ( SimpleSubShell ) :

	intro = '''This shell will properly format shellcode
	pasted from sources like "exploit-db.com" and "msfvenom"'''
	fire_word = 'GO'


	def __init__( self, stream, handler, queue_dict, base_shell, ignore_messages = set(['X']), prompt_templ = "[{stream}]> ") :
		# print ShellcodeSubShell
		SimpleSubShell.__init__( self, stream, handler, queue_dict, base_shell, ignore_messages, prompt_templ )
		self.shellcode_buffer = ''



	def default( self, line ) :
		print
		print "Type '%s' when done pasting..." % self.fire_word

		if line.strip() == self.fire_word :
			if not self.shellcode_buffer :
				print "No shellcode is pasted"
				return

			pure_shellcode = format_shellcode( self.shellcode_buffer )
			self.do_show('')
			if not self.confirm() :
				print "Shellcode NOT sent..."
				print "You can clear the buffer with 'clear'"
				return
			self.handler.preferred_send( pure_shellcode, self.stream )
			self.shellcode_buffer = ''
			return

		self.shellcode_buffer += line+'\n'


	def confirm( self ) :
		option = raw_input("Send the shellcode over? [y/N] ")
	 	return option.lower() == 'y'


	def do_clear( self, line ) :
		self.shellcode_buffer = ''
		print "Buffer cleared!"


	def do_show( self, line ) :
		print self.ruler*20
		show( self.shellcode_buffer )
		print self.ruler*20
