# Default MIRA GUI config

main_window = hsplit(
    docked(
        vsplit(
            panel('status.ScriptStatusPanel'),
            panel('console.ConsolePanel'),
        ),
        # ('Watch Expressions',panel('watch.WatchPanel')),
        ('NICOS devices', panel('devices.DevicesPanel',
                                icons=True, dockpos='right')),
        ('Experiment info',
         panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',
               sample_panel='nicos.clients.gui.panels.setup_panel.TasSamplePanel')),
    ),
)

windows = [
    window('Editor', 'editor', panel('editor.EditorPanel',
                                     tools=[tool('Scan', 'scan.ScanTool')])),
    window('Live data', 'live', panel('mira.gui.live.LiveDataPanel')),
    window('Camera', 'live', panel('liveqwt.LiveDataPanel', instrument='poli')),
    window('Scans', 'plotter', panel('scans.ScansPanel')),
    window('History', 'find', panel('history.HistoryPanel')),
    window('Devices', 'table', panel('devices.DevicesPanel')),
    window('Logbook', 'table', panel('elog.ELogPanel')),
    window('NICOS log files', 'table', panel('logviewer.LogViewerPanel')),
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
    tool(
        'Downtime report',
        'downtime.DownTimeTool',
        receiver = 'f.carsughi@fz-juelich.de',
        mailserver = 'smtp.frm2.tum.de',
        sender = 'mira@frm2.tum.de',
    ),
    cmdtool(
        'Server control panel',
        ['marche-gui', '-B', 'mira1', 'miracascade', 'mira2', 'cascade02']
    ),
    tool('Calculator', 'calculator.CalculatorTool', mieze = MIEZE_settings),
    tool('Neutron cross-sections', 'website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('MIRA Wiki', 'website.WebsiteTool',
         url='http://wiki.frm2.tum.de/mira:index'),
    tool('Phone database', 'website.WebsiteTool',
         url='http://www.mlz-garching.de/ueber-mlz/telefonverzeichnis.html'),
    tool('Report NICOS bug or request enhancement', 'bugreport.BugreportTool'),
]
