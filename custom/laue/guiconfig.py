"""NICOS GUI default configuration."""

main_window = docked(
    vsplit(
        panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
        # panel('nicos.clients.gui.panels.watch.WatchPanel'),
        panel('nicos.clients.gui.panels.console.ConsolePanel'),
    ),
    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True, dockpos='right', )
    ),
    ('Experiment Information and Setup',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel', popup_proposal_after=1. )
    ),
)

windows = [
    window('Editor', 'editor', panel('nicos.clients.gui.panels.editor.EditorPanel')),
    window('Scans', 'plotter', panel('nicos.clients.gui.panels.scans.ScansPanel')),
    window('History', 'find', panel('nicos.clients.gui.panels.history.HistoryPanel')),
    window('Logbook', 'table', panel('nicos.clients.gui.panels.elog.ELogPanel')),
    window('Log files', 'table', panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
    window('Errors', 'errors', panel('nicos.clients.gui.panels.errors.ErrorPanel')),
    window('Live data', 'live',panel('nicos.clients.gui.panels.liveqwt.LiveDataPanel',
                                     cachesize = 40,
                                     showcached = True,
                                     instrument = 'laue',
                                     filetypes=['tif'])),
]

tools = [
    tool('Downtime report', 'nicos.clients.gui.tools.downtime.DownTimeTool',
         receiver='f.carsughi@fz-juelich.de',
         mailserver='smtp.frm2.tum.de',
         sender='laue@frm2.tum.de',
        ),
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Neutron cross-sections', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://forge.frm2.tum.de/redmine/projects/nicos/issues/new'),
    tool('Emergency stop button', 'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=False),
    tool('Esmeralda', 'nicos.clients.gui.tools.commands.AsyncCommandsTool',
          commands=[('Run Esmeralda', '/home/laue/pedersen/esmeralda715/Esmeralda')]
        ),
]
