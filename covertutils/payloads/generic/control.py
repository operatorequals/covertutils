
Commands = {
	'reset' : 'RST',
	'identity' : 'ID',
}

def init( storage ) :
	Commands = {
		'reset' : 'RST',
		'identity' : 'ID',
	}
	storage['commands'] = Commands
	return True

def work( storage, message ) :
	print "Control message: %s" % message
	# command = 
	if message == storage['commands']['reset'] :
		storage['COMMON']['handler'].reset()
		return 'OK'
	elif message ==  storage['commands']['identity'] :
		return storage['COMMON']['handler'].orchestrator.getIdentity()[:8]

	else :
		return "N/A"
