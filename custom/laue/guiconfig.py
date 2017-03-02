"""NICOS GUI default configuration."""

main_window = docked(
    vsplit(
        panel('status.ScriptStatusPanel'),
        # panel('watch.WatchPanel'),
        panel('console.ConsolePanel'),
    ),
    ('NICOS devices',
     panel('devices.DevicesPanel', icons=True, dockpos='right', )
    ),
    ('Experiment Information and Setup',
     panel('expinfo.ExpInfoPanel', )
    ),
)

windows = [
    window('Editor', 'editor', panel('editor.EditorPanel')),
    window('Scans', 'plotter', panel('scans.ScansPanel')),
    window('History', 'find', panel('history.HistoryPanel')),
    window('Logbook', 'table', panel('elog.ELogPanel')),
    window('Log files', 'table', panel('logviewer.LogViewerPanel')),
    window('Errors', 'errors', panel('errors.ErrorPanel')),
    window('Live data', 'live',panel('live.LiveDataPanel',
                                     cachesize = 40,
                                     showcached = True,
                                     instrument = 'laue',
                                     filetypes=['tif',])),
]

tools = [
    tool('Downtime report', 'downtime.DownTimeTool',
# If not at the FRM II facility you have to change this reporting address
         receiver='f.carsughi@fz-juelich.de',
# If you are not at the FRM II facility you have to change your mail server
         mailserver='smtp.frm2.tum.de',
# Please change the sender address to a valid, instrument specific address
         sender='laue@frm2.tum.de',
        ),
    tool('Calculator', 'calculator.CalculatorTool'),
    tool('Neutron cross-sections', 'website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug', 'website.WebsiteTool',
         url='http://forge.frm2.tum.de/redmine/projects/nicos/issues/new'),
    tool('Emergency stop button', 'estop.EmergencyStopTool',
         runatstartup=False),
    tool('Esmeralda', 'nicos.clients.gui.tools.commands.AsyncCommandsTool',
          commands=[('Run Esmeralda', '/home/laue/pedersen/esmeralda715/Esmeralda')]
        ),
]
