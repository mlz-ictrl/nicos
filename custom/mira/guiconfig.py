# Default MIRA GUI config

main_window = vsplit(
    hsplit(
        panel('status.ScriptStatusPanel'),
        tabbed(('Experiment info', panel('expinfo.ExpInfoPanel',
                                         sample_panel='setup_panel.TasSamplePanel')),
               ('Watch expressions', panel('watch.WatchPanel'))),
    ),
    panel('console.ConsolePanel'),
)

windows = [
    # window('Setup', 'setup',
    #        tabbed(('Experiment', panel('setup_panel.ExpPanel')),
    #               ('Setups',     panel('setup_panel.SetupsPanel')),
    #               ('Detectors/Environment', panel('setup_panel.DetEnvPanel')),
    #        )),
    window('Editor', 'editor',
           panel('editor.EditorPanel',
                 tools = [
                     tool('Scan', 'scan.ScanTool')
                 ])),
    window('Live data', 'live',
           panel('mira.gui.live.LiveDataPanel')),
    window('Scans', 'plotter',
           panel('scans.ScansPanel')),
    window('History', 'find',
           panel('history.HistoryPanel')),
    window('Devices', 'table',
           panel('devices.DevicesPanel')),
    window('Logbook', 'table',
           panel('elog.ELogPanel')),
    window('NICOS log files', 'table',
           panel('logviewer.LogViewerPanel')),
]


MIEZE_settings = [
    '46_69',
#    '65_97p5',
#    '74_111',
    '72_108',
#    '103_154p5',
    '99_148p5',
    '138_207',
    '139_208p5_BS',
    '200_300',
    '200_300_BS',
    '279_418p5_BS',
    '280_420',
]

tools = [
    tool('Downtime report', 'downtime.DownTimeTool',
         receiver='f.carsughi@fz-juelich.de',
         mailserver='smtp.frm2.tum.de',
         sender='mira@frm2.tum.de',
        ),
    cmdtool('TACO control panel',
            ['ssh', '-XY', 'maint@mira1', 'sudo', 'tacocp']),
    tool('Calculator', 'calculator.CalculatorTool',
         mieze=MIEZE_settings),
    tool('Neutron cross-sections', 'website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('MIRA Wiki', 'website.WebsiteTool',
         url='http://mira2.mira.frm2:8080/'),
    tool('Phone database', 'website.WebsiteTool',
         url='http://www.mlz-garching.de/ueber-mlz/telefonverzeichnis.html'),
    tool('Report NICOS bug or request enhancement',
         'bugreport.BugreportTool'),
]
