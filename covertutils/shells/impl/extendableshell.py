from covertutils.shells import BaseShell
# from covertutils.shells.impl import BaseShell
# from covertutils.shells.subshells import StageSubShell
from covertutils.shells.subshells import *

from covertutils.helpers import defaultArgMerging


class ExtendableShell (BaseShell) :

	Defaults = {}
	Defaults['subshells'] = {
		'control' : ControlSubShell,
		'python' : PythonAPISubShell,
		'os-shell' : SimpleSubShell,
		'file' : FileSubShell,
		'stage' : StageSubShell,
		}
	Defaults['prompt'] = "({package} v{version})> "

	def __init__( self, handler,
		log_unrecognised = False,
		**kw
		) :
		args = defaultArgMerging(ExtendableShell.Defaults, kw)
		BaseShell.__init__( self, handler, log_unrecognised, **args )
