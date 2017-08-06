# from builtins import chr

from difflib import SequenceMatcher
import abc



class CovertUtilsException( Exception ) :
	'''	General Exception for raising in helper functions	'''
	pass


def sxor( s1, s2 ) :
	if len(s1) != 1 and len(s2) != 1 :
		raise CovertUtilsException( "Incompatible lengths. An Argument is more than 1 char long" )

	return chr(ord(s1) ^ ord(s2))

def xor_str( s1, s2 ) :
	if len(s1) != len(s2) :
		raise CovertUtilsException( "Incompatible lengths. %d != %d" % ( len(s1), len(s2) ) )
	return ''.join(sxor(a,b) for a,b in zip(s1,s2))


def permutate( list_, number_set ) :
	ret = []
	for i in number_set :
		x = list_[i]
		ret.append(x)
	return ret

# taken from:
#	http://stackoverflow.com/questions/17388213/find-the-similarity-percent-between-two-strings
def str_similar(a, b):
	return SequenceMatcher(None, a, b).ratio()



def defaultArgMerging( defaults, kwargs ) :
	ret = {}
	for k in list( defaults.keys() ) :
		try :
			ret[k] = kwargs[k]
		except :
			ret[k] = defaults[k]

	for k in list( kwargs.keys() ) :
		ret[k] = kwargs[k]

	return ret


#	http://stackoverflow.com/questions/3636928/test-if-a-python-string-is-printable
def isprintable( s ) :
	import string
	return all(c in string.printable for c in s)


#	http://stackoverflow.com/questions/13741998/is-there-a-way-to-let-classes-inherit-the-documentation-of-their-superclass-with
def copydoc(fromfunc, sep="\n"):
	"""
	Decorator: Copy the docstring of `fromfunc`
	"""
	def _decorator(func):
		sourcedoc = fromfunc.__doc__
		if sourcedoc == None :
			sourcedoc = ''
		if func.__doc__ == None:
			func.__doc__ = sourcedoc
		else:
			func.__doc__ = sep.join([sourcedoc, func.__doc__])
		return func

	return _decorator
