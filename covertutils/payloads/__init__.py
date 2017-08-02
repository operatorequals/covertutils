import marshal

# print "Importing %s" %  __name__
def dinit( storage ) :
	return 1

def import_payload_from_module( module ) :
	try :
		init = module.init
	except  :
		init = dinit
	work = module.work
	return  init, work


def __str_to_module( module_str ) :
	# print globals()
	ret_mod = __import__(module_str, globals(), locals(), ['object'], -1)
	return ret_mod




def import_stage_from_module_str( module_str ) :
	ret = {}
	module = __str_to_module( module_str )
	ret = import_stage_from_module( module )
	return ret


def import_stage_from_module( module ) :
	init, work = import_payload_from_module (module)
	ret = __form_stage_from_function( init, work )
	try :
		shell_class = module.shell
	except Exception as e:
		# print e, module
		shell_class = None
	ret['shell'] = shell_class		# import the shell in the module if available
	return ret


def __form_stage_from_function( init, work ) :
	ret = {}
	dict_ = {'init' : init, 'work' : work}
	code = {'init' : init.func_code, 'work' : work.func_code}
	ret['object'] = dict_
	ret['python'] = code
	try :
		marshaled = marshal.dumps(code)
	except ValueError:
		marshaled = None

	try :
		import dill
		dilled = dill.dumps(code)
	except ImportError:
		dilled = None
	ret['dill'] = dilled
	ret['marshal'] = marshaled

	return ret

GenericStages, WindowsStages, LinuxStages = None, None, None

def generatePayloads( ) :

	global GenericStages
	global WindowsStages
	global LinuxStages

	LinuxStages = {}
	# LinuxStages['shellcode'] = import_stage_from_module_str('linux.shellcode')
	import linux.shellcode as lshellcode
	LinuxStages['shellcode'] = import_stage_from_module(lshellcode)

	WindowsStages = {}
	# WindowsStages['shellcode'] = import_stage_from_module_str('windows.shellcode')
	import windows.shellcode as wshellcode
	WindowsStages['shellcode'] = import_stage_from_module(wshellcode)


	GenericStages = {}
	# GenericStages['echo'] = import_stage_from_module_str('generic.echo')
	# GenericStages['shell'] = import_stage_from_module_str('generic.shell')
	# GenericStages['shellprocess'] = import_stage_from_module_str('generic.shellprocess')
	# GenericStages['pythonapi'] = import_stage_from_module_str('generic.pythonapi')
	# GenericStages['control'] = import_stage_from_module_str('generic.control')


	import generic.control as control
	GenericStages['control'] = import_stage_from_module(control)
	import generic.shell as shell
	GenericStages['shell'] = import_stage_from_module(shell)
	import generic.shellprocess as shellprocess
	GenericStages['shellprocess'] = import_stage_from_module(shellprocess)
	import generic.pythonapi as pythonapi
	GenericStages['pythonapi'] = import_stage_from_module(pythonapi)
	import generic.echo as echo
	GenericStages['echo'] = import_stage_from_module(echo)
	import generic.file as file_
	GenericStages['file'] = import_stage_from_module(file_)

	return GenericStages, WindowsStages, LinuxStages


generatePayloads()
#
# print GenericStages
# print
# print LinuxStages
# print
# print WindowsStages


# if __name__ == '__main__' :
#
# 	import sys
# 	payload_dicts = [LinuxStages, WindowsStages, GenericStages]
# 	for pload in payload_dicts :
# 		marshal.dumps
