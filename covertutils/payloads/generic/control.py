

def init( storage ) :
	Commands = {
		'reset' : 'RST',
		'identity' : 'ID',
		'sysinfo' : 'SI'
	}
	storage['commands'] = Commands
	return True

def work( storage, message ) :
	print "Control message: %s" % message
	# command =
	if message == storage['commands']['reset'] :
		storage['COMMON']['handler'].reset()
		return 'OK'
	elif message == storage['commands']['identity'] :
		return storage['COMMON']['handler'].orchestrator.getIdentity()[:8]

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
