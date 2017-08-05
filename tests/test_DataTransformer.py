import unittest

from covertutils.datamanipulation import DataTransformer

from random import randint

from struct import pack

class Test_DataTransformer(unittest.TestCase) :

	configuration = [( ('simple:X','simple:X'),('!H','!H'), '_data_+1' )]

	stego_conf = """

X:_data_:

simple='''4142XXXX4344'''

	"""

	def setUp( self ) :
		self.trans = DataTransformer( self.stego_conf, self.configuration )

	def test_transformation (self) :

		data = 'AB\x00\x00CD'
		data2 = self.trans.runAll( data, 'simple' )
		# print data2.encode('hex')
		# self.failAnless
		pass
