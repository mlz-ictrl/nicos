# Default GALAXI GUI config
"""NICOS GUI configuration for GALAXI."""

from nicos.clients.gui.config import hsplit, vsplit, window, panel, tool, tabbed

config = ('Default', [
        hsplit(
            vsplit(
                panel('generic.GenericPanel',
                      uifile = 'custom/galaxi/lib/gui/jcnslogo.ui'),
                panel('expinfo.ExpInfoPanel'),
            ),
            vsplit(
                panel('status.ScriptStatusPanel'),
                panel('console.ConsolePanel'),
            ),
            vsplit(
                panel('devices.DevicesPanel'),
            ),
        ),
        window('Setup', 'setup', True,
            tabbed(('Experiment', panel('setup_panel.ExpPanel')),
                   ('Setups',     panel('setup_panel.SetupsPanel')),
            )),
        window('Editor', 'editor', True,
            vsplit(
                panel('scriptbuilder.CommandsPanel'),
                panel('editor.EditorPanel'))),
        window('Scans', 'plotter', True,
            panel('scans.ScansPanel')),
        window('History', 'find', True,
            panel('history.HistoryPanel')),
        window('Logbook', 'table', True,
            panel('elog.ELogPanel')),
        window('Errors', 'errors', True,
            panel('errors.ErrorPanel')),
    ], [
        tool('Calculator',
             'nicos.clients.gui.tools.calculator.CalculatorTool'),
        tool('Report NICOS bug or request enhancement', 'bugreport.BugreportTool'),
        tool('Emergency stop button', 'estop.EmergencyStopTool',
            runatstartup=True),
    ]
)
