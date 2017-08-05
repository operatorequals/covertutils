import unittest

from covertutils.datamanipulation import StegoInjector
from covertutils.datamanipulation import asciiToHexTemplate

from os import urandom


class Test_StegoInjector(unittest.TestCase):


	def setUp(self):
		pass



	def test_group_str_similarity( self ) :

		config = """
X:_data_:

data1 = '''4444444445454545'''X[2:6]
data2 = "4444XXXXXXXX4545"

		"""
		psi = StegoInjector( config )

		res1 = psi.inject("A"*4, 'data1')
		res2 = psi.inject("A"*4, 'data2')

		# print psi.getCapacity( 'data1' )
		# print res1
		# print res2
		self.failUnless( res1 == res2 )



	def test_injection_from_dict( self, n = 4 ) :

		config = '''
X:_data_:
Y:_sxor_(_data_, '\xaa'):

data1="""44444444%s41414141%s"""
		''' % ("X"*n, "Y"*n)

		inj_dict = { 'X':'a'* (n/2),
					'Y':'b'* (n/2)
				}

		psi = StegoInjector( config )
		stego_pkt = psi.injectByTag(inj_dict, template = 'data1')
		self.failUnless( stego_pkt == 'DDDDaaAAAAbb')



	def test_extraction_from_dict( self, n=4 ) :
		config = '''
X:_data_:
Y:_data_:

data1="""44444444%s41414141%s"""
		''' % ("X"*n, "Y"*n)
		inj_dict = { 'X':'a'* (n/2),
					'Y':'b'* (n/2)
				}
		psi = StegoInjector( config )
		pkt = 'DDDDaaAAAAbb'
		extr_dict = psi.extractByTag( pkt, template = 'data1')

		self.failUnless( inj_dict == extr_dict)


	def test_injection_from_text( self, n = 4) :
		config = '''
X:_data_:
Y:_data_:

data1="""44444444%s41414141%s"""
		''' % ("X"*n, "Y"*n)
		data = 'aabb'
		psi = StegoInjector( config )
		stego_pkt = psi.inject(data, template = 'data1')
		self.failUnless( stego_pkt == 'DDDDaaAAAAbb')


	def test_injection_scramble( self, ) :
		config = '''
X:_data_:
Y:_data_:

data1="""44X44X4141Y4141Y44X43X"""
'''
		data = 'fff'
		psi = StegoInjector( config )
		stego_pkt = psi.inject(data, template = 'data1')

		self.failUnless( stego_pkt.encode('hex').count('6') == 6 )


	def test_injection_scramble( self, ) :
		config = '''
X:_data_:
Y:_data_:

data1="""44X44X4141Y4141Y44X43X"""
'''
		pkt = '4464464141641416446436'.decode('hex')
		psi = StegoInjector( config )
		extr_pkt = psi.extract(pkt, template = 'data1')
		data = 'fff'

		self.failUnless( extr_pkt == data  )





	def test_syntax_multiple_packets( self ) :

		config = '''
X:_data_:
Y:_data_:

data1="""44X44X4141Y4141Y44X43X"""

data2="""44X44X4141Y4141Y44X43X"""
'''
		psi = StegoInjector( config )
		psi.getCapacity('data1')
		psi.getCapacity('data2')


	def test_pattern_guesser( self ) :

		config = '''
X:_data_:
Y:_data_:

data1="""41414141XXYY"""
data2="""41414142XXYY"""
'''
		psi = StegoInjector( config )

		pkt1 = 'AAAAcd'
		pkt2 = 'AAAdfg'

		res, score = psi.guessTemplate( pkt1 )
		# print res

		self.failUnless( res == 'data1' )


	def test_ascii_to_hex_template( self, n = 1000 ) :
		pkt = urandom( n )
		pkt = pkt.replace(pkt[-1], '~')
		pkt = pkt.replace(pkt[-2], '~')
		pkt = pkt.replace(pkt[-3], '~')

		templ = asciiToHexTemplate( pkt )

		config = '''
X:_data_:

data1="""%s"""
''' % templ
		psi = StegoInjector( config )
		cap = psi.getCapacity( 'data1' )
		inj = psi.inject(cap*'~', 'data1' )
		print "Changed %d bytes" % cap
		self.failUnless( inj == pkt )
