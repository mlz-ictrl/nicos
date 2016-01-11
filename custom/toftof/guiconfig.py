"""NICOS GUI default configuration."""

main_window = docked(
    vsplit(
        panel('status.ScriptStatusPanel', stopcounting=True),
#       panel('watch.WatchPanel'),
        panel('console.ConsolePanel'),
    ),
    ('NICOS devices',
     panel('devices.DevicesPanel', icons=True, dockpos='right',),
    ),
    ('Safety system',
     panel('toftof.gui.safetypanel.SafetyPanel'),
    ),
    ('Detector information',
     panel('generic.GenericPanel', uifile='custom/toftof/lib/gui/ratespanel.ui'),
    ),
    ('Experiment Information and Setup',
     panel('expinfo.ExpInfoPanel')
    ),
)

windows = [
    window('Editor', 'editor',
        vsplit(
#           panel('scriptbuilder.CommandsPanel'),
            panel('editor.EditorPanel',
                  tools = [
#                     tool('Scan Generator',
#                          'tools.ScanTool'),
                  ],
                 ),
        ),
    ),
#   window('Setup', 'setup',
#       tabbed(('Experiment', panel('setup_panel.ExpPanel')),
#              ('Setups',     panel('setup_panel.SetupsPanel')),
#              ('Detectors/Environment', panel('setup_panel.DetEnvPanel')),
#       )
#   ),
#   window('Scans', 'plotter', panel('scans.ScansPanel'),),
    window('History', 'find', panel('history.HistoryPanel'),),
    window('Logbook', 'table', panel('elog.ELogPanel'),),
    window('Errors', 'errors', panel('errors.ErrorPanel'),),
    window('Live data', 'live', panel('live.LiveDataPanel',
                                      instrument = 'toftof'),),
]

tools = [
    tool('Downtime report', 'downtime.DownTimeTool',
         receiver='f.carsughi@fz-juelich.de',
         mailserver='smtp.frm2.tum.de',
         sender='toftof@frm2.tum.de',
        ),
    tool('Calculator', 'calculator.CalculatorTool'),
    tool('Neutron cross-sections', 'website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug or request enhancement', 'bugreport.BugreportTool'),
    tool('Emergency stop button', 'estop.EmergencyStopTool',
         runatstartup=False,),
]
