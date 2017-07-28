from covertutils.shells import BaseShell
from covertutils.shells.subshells import *

from covertutils.helpers import defaultArgMerging


class SimpleShell (BaseShell) :

	Defaults = {}
	Defaults['subshells'] = {
		'control' : SimpleSubShell,
		}
	Defaults['prompt'] = "({package} v{version})> "

	def __init__( self, handler,
		log_unrecognised = False,
		**kw
		) :
		args = defaultArgMerging(StandardShell.Defaults, kw)
		BaseShell.__init__( self, handler, log_unrecognised, **args )
