"""
All exception of `covertutils` package are provided centrically in this module.

"""

class TemplateNotFoundException( Exception ) :
	''' This Exception is thrown when the template passed as argument is not available in the :class:`covertutils.datamanipulation.stegoinjector.StegoInjector` configuration string '''


class InvalidChunkException( Exception ) :
	''' Exception thrown when the chunks are invalid '''
	pass



class StreamAdditionException( Exception ) :
	"""	This Exception is thrown if any issue happens in stream addition. """
	pass


class StreamAlreadyExistsException( StreamAdditionException ) :
	"""	This Exception is thrown if an existing stream is tried to be re-added. """
	pass

class StreamDeletionException( Exception ) :
	"""	This Exception is thrown if the deletion of a stream is not possible. """
	pass




class StegoSchemeParseException ( Exception ) :
	'''	This Exception is thrown whenever the StegoScheme syntax gets violated '''
	pass


class StegoDataInjectionException( Exception ) :
	'''	This Exception is thrown whenever given data cannot be properly injected in Data '''
	pass


class StegoDataExtractionException( Exception ) :
	''' This Exception is thrown whenever data extraction from a Data is not possible '''
	pass




class NoFunctionAvailableException( Exception ) :
    """ This Exception is raised when the received stream does not have a corresponding function. """
    pass
