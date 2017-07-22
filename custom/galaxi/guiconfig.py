"""NICOS GUI configuration for GALAXI."""

main_window = hsplit(
    vsplit(
        panel('nicos.clients.gui.panels.generic.GenericPanel',
              uifile = 'custom/galaxi/lib/gui/jcnslogo.ui'),
        panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel'),
    ),
    vsplit(
        panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
        panel('nicos.clients.gui.panels.console.ConsolePanel'),
    ),
    vsplit(
        panel('nicos.clients.gui.panels.devices.DevicesPanel'),
    ),
)

windows = [
    window('Setup', 'setup',
           tabbed(('Experiment',
                   panel('nicos.clients.gui.panels.setup_panel.ExpPanel')),
                  ('Setups',
                   panel('nicos.clients.gui.panels.setup_panel.SetupsPanel'))),
           ),
    window('Editor', 'editor',
           vsplit(
               panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
               panel('nicos.clients.gui.panels.editor.EditorPanel'))),
    window('Scans', 'plotter',
           panel('nicos.clients.gui.panels.scans.ScansPanel')),
    window('History', 'find',
           panel('nicos.clients.gui.panels.history.HistoryPanel')),
    window('Logbook', 'table',
           panel('nicos.clients.gui.panels.elog.ELogPanel')),
    window('Errors', 'errors',
           panel('nicos.clients.gui.panels.errors.ErrorPanel')),
]

tools = [
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Emergency stop button',
         'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=True),
]
