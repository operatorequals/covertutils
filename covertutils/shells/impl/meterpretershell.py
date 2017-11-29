from covertutils.shells.subshells import MeterpreterSubShell
from covertutils.shells import BaseShell

from covertutils.shells.impl import StandardShell

from covertutils.helpers import defaultArgMerging


class MeterpreterShell (BaseShell) :

	Defaults = {}
	Defaults['subshells'] = {
		'meterpreter' : MeterpreterSubShell,
		}
	# Defaults['prompt'] = "({package} v{version})> "

	def __init__( self, handler,
		**kw
		) :
		handler.getOrchestrator().addStream('meterpreter')
		handler.getOrchestrator().streamIdent.setHardStreamName('meterpreter')

		handler.getOrchestrator().deleteStream('control')
		args = defaultArgMerging(MeterpreterShell.Defaults, kw)
		BaseShell.__init__( self, handler, **args )
