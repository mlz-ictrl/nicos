# Default MIRA GUI config

main_window = hsplit(
    docked(
        vsplit(
            panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
            panel('nicos.clients.gui.panels.console.ConsolePanel'),
        ),
        # ('Watch Expressions',
        #  panel('nicos.clients.gui.panels.watch.WatchPanel')),
        ('NICOS devices',
         panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True,
               dockpos='right')),
        ('Experiment info',
         panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',
               sample_panel='nicos.clients.gui.panels.setup_panel.TasSamplePanel')),
    ),
)

windows = [
    window('Editor', 'editor',
           panel('nicos.clients.gui.panels.editor.EditorPanel',
                 tools=[tool('Scan', 'nicos.clients.gui.tools.scan.ScanTool')])),
    window('Live data', 'live', panel('nicos_mlz.mira.gui.live.LiveDataPanel')),
    window('Camera', 'live',
           panel('nicos.clients.gui.panels.liveqwt.LiveDataPanel',
                 instrument='poli')),
    window('Scans', 'plotter',
           panel('nicos.clients.gui.panels.scans.ScansPanel')),
    window('History', 'find',
           panel('nicos.clients.gui.panels.history.HistoryPanel')),
    window('Devices', 'table',
           panel('nicos.clients.gui.panels.devices.DevicesPanel')),
    window('Logbook', 'table',
           panel('nicos.clients.gui.panels.elog.ELogPanel')),
    window('NICOS log files', 'table',
           panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
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
    tool('Downtime report', 'nicos.clients.gui.tools.downtime.DownTimeTool',
         receiver = 'f.carsughi@fz-juelich.de',
         mailserver = 'smtp.frm2.tum.de',
         sender = 'mira@frm2.tum.de',
    ),
    cmdtool('Server control panel',
            ['marche-gui', '-B', 'mira1', 'miracascade', 'mira2', 'cascade02']
    ),
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool',
         mieze = MIEZE_settings),
    tool('Neutron cross-sections',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('MIRA Wiki', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://wiki.frm2.tum.de/mira:index'),
    tool('Phone database', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.mlz-garching.de/ueber-mlz/telefonverzeichnis.html'),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
]
