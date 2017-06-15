import cmd
from covertutils.prompts import BasePrompt
import covertutils

from covertutils.helpers import defaultArgMerging



def _dummyprint( message ) :
	print
	print message


class PrintPrompt( BasePrompt ) :

	def __init__( self, handler, **kwargs ) :


		if 'message_function_dict' in kwargs.keys() :
			message_function_dict = kwargs['message_function_dict']
		else :
			message_function_dict = {}

		for stream in handler.getOrchestrator().getStreams() :
			if stream not in message_function_dict.keys() :
				message_function_dict[stream] = _dummyprint

		kwargs['message_function_dict'] = message_function_dict
		#
		# arguments = defaultArgMerging(self.Defaults, kwargs)
		# kwargs['message_function_dict'] = arguments['message_function_dict']

		# kwargs['log_messages'] = True
		# kwargs['log_chunks'] = False
		# kwargs['log_unrecognised'] = True
		BasePrompt.__init__( self, handler, **kwargs )
