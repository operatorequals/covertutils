from covertutils.shells.subshells import MeterpreterSubShell
from covertutils.shells.subshells import ControlSubShell
from covertutils.shells import BaseShell


from covertutils.helpers import defaultArgMerging


class MeterpreterShell (BaseShell) :

	Defaults = {}
	Defaults['subshells'] = {
		'control' : ControlSubShell,
		'meterpreter' : MeterpreterSubShell,
		}
	# Defaults['prompt'] = "({package} v{version})> "

	def __init__( self, handler,
		**kw
		) :
		# handler.getOrchestrator().addStream('meterpreter')
		# handler.getOrchestrator().streamIdent.setHardStreamName('meterpreter')
		# handler.getOrchestrator().deleteStream('control')

		args = defaultArgMerging(MeterpreterShell.Defaults, kw)
		BaseShell.__init__( self, handler, **args )
