"""
This code isn't really useful and it is meant to be a guide for making custom `stages` using the `covertutils` API
"""
def init(storage) :
	'''
:param dict storage: The storage object is the only persistent object between runs of both `init()` and `work()`. It is treated as a "Local Storage" for the `stage`.
:return: This function must **always** return True if the initialization is succesfull. If `False` values are returned the `stage` doesn't start and `work()` is never called.
	'''
	print "Initializing stage!"
	"""Saving an arbitrary value to communicate with ``work()`` function"""
	storage['counter'] = 0
	return True


def work(storage, message) :
	'''
:param dict storage: The storage object is the only persistent object between runs of both `init()` and `work()`. It is treated as a "Local Storage" for the `stage`.
:param str message: The data sent from the `Handler` to that `stage`.
:rtype: str
:return: The response to message that arrived. This exact response will reach the `Handler` in the other side.
	'''
	print "Running for handler's message '%s'" % message
	"""Keep state of how many messages have arrived. The `storage` `dict` gets preserved through function calls"""
	storage['counter'] += 1
	print "Returning the message in reverse"
	return "{count} - {response}".format(count = storage['counter'], response = message[::-1])	# Reversing the output


"""	Defining a specific SubShell for the `stage`	"""
from covertutils.shells.subshells import ExampleSubShell as shell
