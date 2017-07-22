"""NICOS GUI configuration for GALAXI."""

main_window = hsplit(
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
)

windows = [
    window('Setup', 'setup',
           tabbed(('Experiment', panel('setup_panel.ExpPanel')),
                  ('Setups',     panel('setup_panel.SetupsPanel'))),
           ),
    window('Editor', 'editor',
           vsplit(
               panel('scriptbuilder.CommandsPanel'),
               panel('editor.EditorPanel'))),
    window('Scans', 'plotter',
           panel('scans.ScansPanel')),
    window('History', 'find',
           panel('history.HistoryPanel')),
    window('Logbook', 'table',
           panel('elog.ELogPanel')),
    window('Errors', 'errors',
           panel('errors.ErrorPanel')),
]

tools = [
    tool('Calculator', 'calculator.CalculatorTool'),
    tool('Report NICOS bug or request enhancement', 'bugreport.BugreportTool'),
    tool('Emergency stop button', 'estop.EmergencyStopTool',
         runatstartup=True),
]
