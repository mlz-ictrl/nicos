"""NICOS GUI configuration for ANTARES."""

main_window = docked(
    vsplit(
        panel('status.ScriptStatusPanel'),
#       panel('watch.WatchPanel'),
        panel('console.ConsolePanel'),
    ),
    ('Experiment Info',
        panel('expinfo.ExpInfoPanel'),
    ),
    ('Devices',
        panel('devices.DevicesPanel'),
    ),
)

windows = [
        window('Setup', 'setup',
            tabbed(('Experiment', panel('setup_panel.ExpPanel')),
                   ('Setups',     panel('setup_panel.SetupsPanel')),
                   ('Detectors/Environment', panel('setup_panel.DetEnvPanel')),
            )),
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
        window('Live data', 'live',
            panel('live.LiveDataPanel',
                  instrument = 'imaging')),
]

tools = [
        tool('Downtime report', 'downtime.DownTimeTool',
             receiver='f.carsughi@fz-juelich.de',
             mailserver='smtp.frm2.tum.de',
             sender='antares@frm2.tum.de',
            ),
        tool('Calculator', 'calculator.CalculatorTool'),
        tool('Neutron cross-sections', 'website.WebsiteTool',
             url='http://www.ncnr.nist.gov/resources/n-lengths/'),
        tool('Neutron activation', 'website.WebsiteTool',
             url='https://webapps.frm2.tum.de/intranet/activation/'),
        tool('Neutron calculations', 'website.WebsiteTool',
             url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
        tool('Report NICOS bug or request enhancement', 'bugreport.BugreportTool'),
        tool('Maintenance commands', 'commands.CommandsTool',
             commands=[
                 ('TACO server control panel (beta)', 'SSH_ASKPASS=/usr/bin/ssh-askpass setsid /usr/bin/ssh -XY maint@antareshw.antares.frm2 "source /etc/tacoenv.sh && sudo /usr/bin/python /opt/tacocp/tacocp.py antaressrv.antares.frm2" && exit'),
             ]),
]
