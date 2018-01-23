"""NICOS GUI default configuration."""

main_window = docked(
    vsplit(
        panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
        # panel('nicos.clients.gui.panels.watch.WatchPanel'),
        panel('nicos.clients.gui.panels.console.ConsolePanel'),
    ),
    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True,
           dockpos='right',)
    ),
    ('Experiment Information and Setup',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',)
    ),
)

windows = [
    window('Editor', 'editor',
           panel('nicos.clients.gui.panels.editor.EditorPanel')),
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
           panel('nicos_mlz.spodi.gui.panels.live.LiveDataPanel')),
]

tools = [
    tool('Downtime report', 'nicos.clients.gui.tools.downtime.DownTimeTool',
# If not at the FRM II facility you have to change this reporting address
         receiver='f.carsughi@fz-juelich.de',
# If you are not at the FRM II facility you have to change your mail server
         mailserver='smtp.frm2.tum.de',
# Please change the sender address to a valid, instrument specific address
         sender='spodi@frm2.tum.de',
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
