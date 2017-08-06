import unittest

from covertutils.datamanipulation import DataTransformer

from random import randint

from struct import pack

class Test_DataTransformer(unittest.TestCase) :

	configuration = [( ('simple:X','simple:X'),('!H','!H'), '_data_+1' )]

	stego_conf = """
X:_data_:

simple='''41420000XXXX'''

	"""

	def setUp( self ) :
		self.trans = DataTransformer( self.stego_conf, self.configuration )


	def test_transformation (self) :
		data = 'AB\x00\x00CD'
		data2 = self.trans.runAll( data, 'simple' )
		alt_part = data2.encode('hex')[-4:]
		print( data2.encode('hex') )
		self.assertTrue( alt_part == '4345') # added 1 to 4344
