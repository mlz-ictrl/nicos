# Default POWTEX GUI config
"""NICOS GUI configuration for POWTEX."""

main_window = docked(
    hsplit(
        vsplit(
#           panel('generic.GenericPanel',
#                 uifile = 'custom/jcns/lib/gui/jcnslogo.ui'),
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
)

windows = [
    window('Setup', 'setup', True,
        tabbed(('Experiment', panel('setup_panel.ExpPanel')),
               ('Setups', panel('setup_panel.SetupsPanel')),
        ),
    ),
    window('Editor', 'editor', True,
        vsplit(
            panel('scriptbuilder.CommandsPanel'),
            panel('editor.EditorPanel'),
        ),
    ),
    window('Scans', 'plotter', True,
            panel('scans.ScansPanel'),
    ),
    window('History', 'find', True,
            panel('history.HistoryPanel'),
    ),
    window('Logbook', 'table', True,
            panel('elog.ELogPanel'),
    ),
    window('Errors', 'errors', True,
            panel('errors.ErrorPanel'),
    ),
]

tools = [
    tool('Downtime report', 'downtime.DownTimeTool',
# If not at the FRM-II facility you have to change this reporting address
         receiver='f.carsughi@fz-juelich.de',
# If you are not at the FRM-II facility you have to change your mail server
         mailserver='smtp.frm2.tum.de',
# Please change the sender address to a valid, instrument specific address
         sender='powtex@frm2.tum.de',
        ),
    tool('Calculator', 'calculator.CalculatorTool'),
    tool('Emergency stop button', 'estop.EmergencyStopTool',
         runatstartup = True),
]
