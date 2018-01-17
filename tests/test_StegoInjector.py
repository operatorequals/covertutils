import unittest

from covertutils.datamanipulation import StegoInjector
from covertutils.datamanipulation import asciiToHexTemplate

from os import urandom
import codecs

from covertutils.exceptions import *


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

		self.assertTrue( res1 == res2 )



	def test_injection_from_dict( self, n = 100 ) :

		for i in range( 2, n, 2  ) :
			config = '''
	X:_data_:
	Y:_sxor_(_data_, '\xaa'):

	data1="""44444444%s41414141%s"""
			''' % ("X"*i, "Y"*i)

			inj_dict = { 'X':'a'* (i//2),
						'Y':'b'* (i//2)
					}

			psi = StegoInjector( config )
			stego_pkt = psi.injectByTag(inj_dict, template = 'data1')
			testable = 'DDDD%sAAAA%s' % ('a' * (i//2), 'b' * (i//2))

			# print( stego_pkt, testable )
			extr_dict = psi.extractByTag( stego_pkt, 'data1' )
			# print( extr_dict, inj_dict )
			self.assertTrue( extr_dict == inj_dict )


	def test_injection_from_dict_with_template( self, n = 100 ) :

		for i in range( 2, n, 2  ) :
			config = '''
	X:_data_:
	Y:_sxor_(_data_, '\xaa'):

	data1="""44444444%s41414141%s"""
			''' % ("X"*i, "Y"*i)

			inj_dict = { 'X':'a'* (i//2),
						'Y':'b'* (i//2)
					}

			psi = StegoInjector( config )

			templ_pkt = psi.inject('\x00' * i, 'data1')
			print templ_pkt, "<----"

			stego_pkt = psi.injectByTag(inj_dict, template = 'data1', pkt = templ_pkt)
			testable = 'DDDD%sAAAA%s' % ('a' * (i//2), 'b' * (i//2))

			# print( stego_pkt, testable )
			extr_dict = psi.extractByTag( stego_pkt, 'data1' )
			# print( extr_dict, inj_dict )
			self.assertTrue( extr_dict == inj_dict )


	def test_extraction_from_dict( self, n = 4 ) :
		config = '''
X:_data_:
Y:_data_:

data1="""44444444%s41414141%s"""
		''' % ("X"*n, "Y"*n)
		inj_dict = { 'X':'a'* (n//2),
					'Y':'b'* (n//2)
				}
		psi = StegoInjector( config )
		pkt = 'DDDDaaAAAAbb'
		extr_dict = psi.extractByTag( pkt, template = 'data1')

		self.assertTrue( inj_dict == extr_dict)


	def test_injection_from_text( self, n = 4) :
		config = '''
X:_data_:
Y:_data_:

data1="""44444444%s41414141%s"""
		''' % ("X"*n, "Y"*n)
		data = 'aabb'
		psi = StegoInjector( config )
		stego_pkt = psi.inject(data, template = 'data1')
		self.assertTrue( stego_pkt == 'DDDDaaAAAAbb')


	def test_injection_scramble( self, ) :
		config = '''
X:_data_:
Y:_data_:

data1="""44X44X4141Y4141Y44X43X"""
'''
		data = 'fff'	# 0x660x660x66
		psi = StegoInjector( config )
		stego_pkt = psi.inject(data, template = 'data1')

		self.assertTrue( stego_pkt.encode('hex').count('6') == 6 )


	def test_injection_equivalence( self ) :
		config = '''
X:_data_:
Y:_sxor_(_data_, chr(_index_) ):

data1 = """XXXXYYYY"""
		'''
		psi = StegoInjector( config )
		data = "\x00"*4
		data_dict = { 'X' : "\x00" * 2, 'Y' : '\x00' * 2}

		pkt1 = psi.inject(data, 'data1')
		pkt2 = psi.injectByTag( data_dict, 'data1' )
		# print( pkt1.encode('hex'), pkt2.encode('hex') )
		self.assertTrue( pkt1 == pkt2 )
		extr1 = psi.extract( pkt1, 'data1' )
		extr_dict = psi.extractByTag( pkt2, 'data1' )
		self.assertTrue( data == extr1 )
		self.assertTrue( data_dict == extr_dict )


	def test_injection_scramble2( self, ) :
		config = '''
X:_data_:
Y:_data_:

data1="""44X44X4141Y4141Y44X43X"""
'''
		pkt = codecs.decode('4464464141641416446436', 'hex')
		psi = StegoInjector( config )
		extr_pkt = psi.extract(pkt, template = 'data1')
		data = 'fff'

		self.assertTrue( extr_pkt == data  )





	def test_syntax_multiple_packets( self ) :

		config = '''
X:_data_:
Y:_data_:

data1="""44X44X4141Y4141Y44X43X"""

data2="""44X44X4141Y4141Y44X43X"""
'''
		psi = StegoInjector( config )
		cap1 = psi.getCapacity('data1')
		cap2 = psi.getCapacity('data2')



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
		# print( res )

		self.assertTrue( res == 'data1' )



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
		print( "Changed %d bytes" % cap )
		self.assertTrue( inj == pkt )



	def test_syntax( self ) :
		conf1 = "la:_data_:" # 2 letter tag
		try :
			p = StegoInjector( conf1 )
		except Exception as e :
			self.assertTrue ( type(e) == StegoSchemeParseException )

		conf2 = "C:_data_:" # Hex Letter
		try :
			p = StegoInjector( conf2 )
		except Exception as e :
			self.assertTrue ( type(e) == StegoSchemeParseException )


	def test_injection_with_pkt( self ) :
		config = '''
X:_data_:
Y:_data_:

data1="""44X44X4141Y4141Y44X43X"""

data2="""44X44X4141Y4141Y44X43X"""
'''
		psi = StegoInjector( config )

		pkt = "\xFF"*11

		inj_pkt = psi.inject( "\x00"*3, 'data1', pkt )

		# print( inj_pkt.encode('hex') )
		testable = "\xFF\x0F\xF0\xFF\xFF\x0F\xFF\xF0\xFF\x0F\xF0"
		# print( testable.encode('hex') )
		self.assertTrue( inj_pkt == testable)



	def test_injection_from_text_to_hex( self, n = 4) :
		config = '''
X:_data_:
Y:_data_:

data1="""44444444%s41414141%s"""
		''' % ("X"*n, "Y"*n)
		data = 'aa'
		psi = StegoInjector( config, hex_inject = True )
		stego_pkt = psi.inject(data, template = 'data1')

		extracted = psi.extract( stego_pkt, 'data1' )
		self.assertTrue( extracted == data )
		# self.assertTrue( stego_pkt == 'DDDD61AAAA61')
