import cmd
import re
import imp
import traceback

from covertutils.shells.subshells import SimpleSubShell		# fallback shell
from covertutils.handlers import StageableHandler		# For the static method

from covertutils.payloads import import_stage_from_module, import_stage_from_module_str



class StageSubShell ( SimpleSubShell ) :

	def __init__( self, stream, handler, queue_dict, base_shell, ignore_messages = set(['X']), prompt_templ = " (-){stream}(+)> ") :
		SimpleSubShell.__init__( self, stream, handler, queue_dict, base_shell, ignore_messages, prompt_templ )
		self.updatePrompt( )

	def default( self, line ) :

		if not line :
			# usage
			return


	def __remoteLoadModule( self, stream_name, stage_obj ) :
		stage_message = StageableHandler.createStageMessage(stream_name, stage_obj['marshal'])
		self.handler.preferred_send( stage_message, StageableHandler.Defaults['stage_stream'] )


	def __localLoadModule( self, stream_name, stage ) :

		try :
			shell_class = stage['shell']
		except :
			shell_class = None
		print shell_class
		if shell_class == None :
			shell_class = SimpleSubShell
		kwargs = {}
		self.base_shell.addSubShell( stream_name, shell_class, kwargs )


	def do_fload( self, line ) :

		if not line :
			# usage
			return
		toks = line.split()
		filename = toks[0]
		stream_name = ''.join(filename.split('/')[-1].split('.')[:-1])	# for /tmp/great.shell.stage.py : great.shell.stage
		# try :
		try :
			stage_mod = imp.load_source('stage', filename)
			stage_dict = import_stage_from_module( stage_mod )
			self.__remoteLoadModule( stream_name, stage_dict )
			self.__localLoadModule( stream_name, stage_dict )
		except Exception as e:
			print "File '%s' could not be loaded!" %  filename
			traceback.print_exc()
			print e
			return

		return


	def do_mload( self, line ) :

		if not line :
			# usage
			return
		toks = line.split()
		stage_mod_name = toks[0]
		stream_name = ''.join(stage_mod_name.split('.')[-1])	# for /tmp/great.shell.stage.py : great.shell.stage
		try :
			stage_dict = import_stage_from_module_str( stage_mod_name )
			self.__remoteLoadModule( stream_name, stage_dict )
			self.__localLoadModule( stream_name, stage_dict )
		except Exception as e:
			print "Module '%s' could not be loaded!" %  stage_mod_name
			traceback.print_exc()
			print e
			return
		return


	def help_fload( self ) :
		print "fload usage:"
		print "\tfload <filepath>"
		print "fload example:"
		print "\tfload /tmp/code.py"


	def help_mload( self ) :
		print "mload usage:"
		print "\tmload <module>"
		print "mload example:"
		print "\tmload covertutils.payloads.windows.shellcode"
