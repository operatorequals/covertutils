def work( storage, message ) :
	from os import popen

	try :
		result = popen( message ).read()
		return result
	except Exception as e :
		return "Module Exception: " + repr(e)
