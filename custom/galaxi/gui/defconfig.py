# Default GALAXI GUI config
from nicos.clients.gui.config import docked, vsplit, panel, window, tool

main_window = docked(
	vsplit(
		panel('status.ScriptStatusPanel'),
		panel('console.ConsolePanel'),
	),
	('JCNS Logo', panel('generic.GenericPanel',
                        uifile='custom/galaxi/lib/gui/jcnslogo.ui',
                       ),
    ),
	('NICOS devices', panel('devices.DevicesPanel', icons=True))
)
windows = [
    window('Editor', 'editor',
        vsplit(
            panel('scriptbuilder.CommandsPanel'),
            panel('editor.EditorPanel'),
        )
    ),
    window('Scans', 'plotter', panel('scans.ScansPanel')),
]
tools = [
    tool('Calculator', 'calculator.CalculatorTool'),
    tool('Report NICOS bug', 'website.WebsiteTool',
         url='http://trac.frm2.tum.de/redmine/projects/nicos/issues/new',
        ),
]
