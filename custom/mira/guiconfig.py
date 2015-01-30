# Default MIRA GUI config

from nicos.clients.gui.config import vsplit, hsplit, panel, window, tool, tabbed

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
    # window('Setup', 'setup', True,
    #        tabbed(('Experiment', panel('setup_panel.ExpPanel')),
    #               ('Setups',     panel('setup_panel.SetupsPanel')),
    #               ('Detectors/Environment', panel('setup_panel.DetEnvPanel')),
    #        )),
    window('Editor', 'editor', True,
           panel('editor.EditorPanel',
                 tools = [
                     tool('Scan', 'nicos.clients.gui.tools.scan.ScanTool')
                 ])),
    window('Live data', 'live', True,
           panel('nicos.mira.gui.live.LiveDataPanel')),
    window('Scans', 'plotter', True,
           panel('scans.ScansPanel')),
    window('History', 'find', True,
           panel('history.HistoryPanel')),
    window('Devices', 'table', True,
           panel('devices.DevicesPanel')),
    window('Logbook', 'table', True,
           panel('elog.ELogPanel')),
    window('NICOS log files', 'table', True,
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
    tool('TACO control panel',
         'ssh -XY maint@mira1 sudo tacocp'),
    tool('Calculator',
         'nicos.clients.gui.tools.calculator.CalculatorTool',
         mieze=MIEZE_settings),
    tool('Neutron cross-sections',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.frm2.tum.de/intranet/neutroncalc/'),
    tool('MIRA Wiki',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://mira2.mira.frm2:8080/'),
    tool('Phone database',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.frm2.tum.de/intern/funktionen/phonedb/index.html'),
    tool('Report NICOS bug or request enhancement', 'bugreport.BugreportTool'),
#    tool('Report NICOS bug',
#         'nicos.clients.gui.tools.website.WebsiteTool',
#         url='http://trac.frm2.tum.de/redmine/projects/nicos/issues/new'),
]
