from covertutils.shells import BaseShell
from covertutils.shells.subshells import ControlSubShell, PythonAPISubShell, SimpleSubShell

from covertutils.helpers import defaultArgMerging


class StandardShell (BaseShell) :

	Defaults = {}
	Defaults['subshells'] = {
		'control' : ControlSubShell,
		'python' : PythonAPISubShell,
		'os-shell' : SimpleSubShell,
		}
	Defaults['prompt'] = "({package} v{version})> "

	def __init__( self, handler,
		log_unrecognised = False,
		**kw
		) :
		args = defaultArgMerging(StandardShell.Defaults, kw)
		BaseShell.__init__( self, handler, log_unrecognised, **args )
		self.sysinfo = None
