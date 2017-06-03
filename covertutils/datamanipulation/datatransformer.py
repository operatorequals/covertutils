from covertutils.datamanipulation import StegoInjector

from struct import pack, unpack


class DataTransformer :
	"""
This class provides automated data transformations.
It uses the :class:`covertutils.datamanipulation.stegoinjector.StegoInjector` class to create alterations to existing data chunks.

**Transformation List**

The Transformation List argument is a specially structured list to dictate to the `DataTranformer` which changes should be done to data packet.
Specifically, for a SYN - (RST, ACK) sequence to be simulated, the following configuration should be used:

.. code:: python

	X:_data_:
	L:_data_:
	K:_data_:

	ip_tcp_syn = '''45000028LLLL000040067ccd7f0000017f000001XXXX0050KKKKKKKK0000000050022000917c0000'''

	ip_tcp_rst_ack = '''450000280001000040067ccd7f0000017f0000010014005000000000XXXXXXXXXX50142000916a0000'''

The Transformation List that has to be used should dictate the class to:

 - Unpack Sequence Number from `ip_tcp_syn` template (K tag)
 - Increment it by 1
 - Place it to a `ip_tcp_rst_ack` template (X tag)
 - All the above while handling **endianess**, **integer overflow checks**, etc

The `transformation_list` is declared below:

.. code:: python

	transformation_list = [ (	# Tranformation #1
		( 'ip_tcp_syn:K', 'ip_tcp_rst_ack:X' ),		# From template:tag to template:tag
		('!I','!I')		# Unpack as an 4-byte Integer (reverse Endianess as of network Endianess) and pack it to 4-byte Integer (reverse Endianess again)
		'_data_ + 1'	# Eval this string (with the extracted/unpacked data as '_data_') and pack the result.
		),
			# No other transformations
	]

"""
	def __init__( self, stego_configuration, transformation_list ) :
		"""
:param str stego_configuration: The Stego Configuration to initialize the internal :class:`covertutils.datamanipulation.stegoinjector.StegoInjector` object.
:param list transformation_list: The Tranformation List as described above.

		"""
		self.injector = StegoInjector( stego_configuration )
		self.transformation_list = transformation_list


	def runAll( self, pkt, template = None ) :
		"""
Runs all Tranformations in the `transformation_list` that relate to the specified template.

:param str pkt: The data packet to run the Tranformations on. In `Raw Bytes`.
:param str template: The template string that describes the given data packet. If `None` the :func:`covertutils.datamanipulation.stegoinjector.StegoInjector.guessTemplate` function will try to guess the correct template.
:rtype: str
:return: Returns the `pkt` with all the related tranformations applied.
		"""
		if not template :
			template = self.injector.guessTemplate( pkt )

		for trans_tuple in self.transformation_list :

			templates, struct_strs, eval_str = trans_tuple
			(out_template_tag, in_template_tag) = templates
			out_template, out_tag = out_template_tag.split(':')
			in_template, in_tag = in_template_tag.split(':')
 			(out_struct, in_struct) = struct_strs

			# if template != out_template :
			# 	continue

			out_data = self.injector.extractByTag( pkt, template )[ out_tag ]
			structed_data = unpack( out_struct, out_data )[0]
#		==========================
			_data_ = structed_data
			output_data = eval( eval_str )
			# print structed_data, eval_str, output_data
#		==========================
			injectable_data = pack( in_struct, output_data )
			# injectable_dict = {'X' : injectable_data }
			# print injectable_data.encode('hex')
			# print self.injector.getCapacity( template ), len( injectable_data)
			# pkt = self.injector.injectByTag( injectable_dict, template, pkt  )
			pkt = self.injector.inject( injectable_data, template, pkt  )

		return pkt
