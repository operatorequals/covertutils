import marshal


def dinit( storage ) :
	return 1

def import_payload_from_module( module_str ) :
	module = __import__(module_str, globals(), locals(), ['object'], -1)
	init_str = "%s.init" % module_str
	work_str = "%s.work" % module_str
	try :
		init = module.init
	except  :
		init = dinit
	work = module.work
	return  init, work



def import_stage_from_module( module_str ) :
	ret = {}
	init, work = import_payload_from_module (module_str)
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
	ret['dilled'] = dilled
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
