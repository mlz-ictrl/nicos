"""NICOS GUI default configuration."""

main_window = docked(
    vsplit(
        panel('nicos.clients.gui.panel.status.ScriptStatusPanel'),
        # panel('nicos.clients.gui.panel.watch.WatchPanel'),
        panel('nicos.clients.gui.panel.console.ConsolePanel'),
    ),
    ('NICOS devices',
     panel('nicos.clients.gui.panel.devices.DevicesPanel', icons=True,
           dockpos='right',)
    ),
    ('Experiment Information and Setup',
     panel('nicos.clients.gui.panel.expinfo.ExpInfoPanel',)
    ),
)

windows = [
    window('Editor', 'editor',
           panel('nicos.clients.gui.panel.editor.EditorPanel')),
    window('Scans', 'plotter',
           panel('nicos.clients.gui.panel.scans.ScansPanel')),
    window('History', 'find',
           panel('nicos.clients.gui.panel.history.HistoryPanel')),
    window('Logbook', 'table',
           panel('nicos.clients.gui.panel.elog.ELogPanel')),
    window('Log files', 'table',
           panel('nicos.clients.gui.panel.logviewer.LogViewerPanel')),
    window('Errors', 'errors',
           panel('nicos.clients.gui.panel.errors.ErrorPanel')),
]

tools = [
    tool('Downtime report', 'nicos.clients.gui.tools.downtime.DownTimeTool',
         receiver='f.carsughi@fz-juelich.de',
         mailserver='smtp.frm2.tum.de',
         sender='mephisto@frm2.tum.de',
        ),
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Neutron cross-sections',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Emergency stop button',
         'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=False),
]
