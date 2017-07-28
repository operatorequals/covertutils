import marshal


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
	return __import__(module_str, globals(), locals(), ['object'], -1)



def import_stage_from_module( module_str ) :
	ret = {}
	module = __str_to_module( module_str )
	init, work = import_payload_from_module (module)
	return __form_stage_from_function( init, work )





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




GenericStages = {}
GenericStages['echo'] = import_stage_from_module('generic.echo')
GenericStages['shell'] = import_stage_from_module('generic.shell')
GenericStages['shellprocess'] = import_stage_from_module('generic.shellprocess')
GenericStages['pythonapi'] = import_stage_from_module('generic.pythonapi')
GenericStages['control'] = import_stage_from_module('generic.control')

LinuxStages = {}
LinuxStages['shellcode'] = import_stage_from_module('linux.shellcode')

WindowsStages = {}
WindowsStages['shellcode'] = import_stage_from_module('windows.shellcode')
#
# print GenericStages
# print
# print LinuxStages
# print
# print WindowsStages
