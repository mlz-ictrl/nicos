"""NICOS GUI default configuration."""

main_window = docked(
    vsplit(
        panel('nicos.clients.gui.panels.cmdbuilder.CommandPanel',
              modules=['nicos.clients.gui.cmdlets'],
        ),
        panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
        panel('nicos.clients.gui.panels.console.ConsolePanel',
              hasinput=False),
    ),
    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True,
           dockpos='right',
           param_display={
               'hv': ['heatercurrent', 'waterflow'],
               'd8': ['ldoor', 'rdoor'],
           },
           ),
    ),
    ('Experiment Information and Setup',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel'),
    ),
)

windows = [
    window('Editor', 'editor',
        vsplit(
           panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
           panel('nicos.clients.gui.panels.editor.EditorPanel',
           ))),
    window('Scans', 'plotter',
           panel('nicos.clients.gui.panels.scans.ScansPanel')),
    window('History', 'find',
           panel('nicos.clients.gui.panels.history.HistoryPanel')),
    window('Logbook', 'table',
           panel('nicos.clients.gui.panels.elog.ELogPanel')),
    window('Log files', 'table',
           panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
    window('Errors', 'errors',
           panel('nicos.clients.gui.panels.errors.ErrorPanel')),
    window('Live data', 'live',
           panel('nicos_mlz.labs.physlab.xresd.gui.live.AutoScaleLiveDataPanel')),
]

tools = [
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Emergency stop button',
         'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=False),
]
