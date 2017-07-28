


def __system_info( storage, message ) :
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
