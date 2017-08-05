import unittest

from covertutils.datamanipulation import DataTranformer



class Test_DataTranformer(unittest.TestCase) :

	configuration = [( ('simple','simple'),('!H','!H'), '_data_+1' )]

	stego_conf = """

X:_data_:

simple='''4142XXXX4344'''

	"""

	def setUp( self ) :
		self.trans = DataTranformer( self.stego_conf, self.configuration )

	def test (self) :

		data = 'AB\x00\x00CD'
		data2 = self.trans.runAll( data, 'simple' )
		print data2.encode('hex')
		# self.failAnless
		pass
