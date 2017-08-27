# from builtins import chr

from difflib import SequenceMatcher
import abc



class CovertUtilsException( Exception ) :
	'''	General Exception for raising in helper functions	'''
	pass


def sxor( s1, s2 ) :
	if len(s1) != 1 and len(s2) != 1 :
		raise CovertUtilsException( "Incompatible length" )

	return chr(ord(s1) ^ ord(s2))


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
	return ret


#	http://stackoverflow.com/questions/3636928/test-if-a-python-string-is-printable
def isprintable( s ) :
	import string
	return all(c in string.printable for c in s)



# 
#
# class DocABCMeta(type):
#
# 	# def __init__(s)
#     def __new__(mcls, classname, bases, cls_dict):
#         cls = type.__new__(mcls, classname, bases, cls_dict)
#         for name, member in cls_dict.items():
#             if not getattr(member, '__doc__'):
#                 member.__doc__ = getattr(bases[-1], name).__doc__
#         return cls
