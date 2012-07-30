# Default MIRA GUI config

from nicos.gui.config import vsplit, hsplit, panel, window, tool

maint_commands = [
    ('Restart NICOS poller',
     'ssh maint@mira1 sudo /etc/init.d/nicos-system restart poller'),
    ('Restart NICOS daemon',
     'ssh maint@mira1 sudo /etc/init.d/nicos-system restart daemon'),
    ('Restart MIRA1 TACO servers',
     'ssh maint@mira1 sudo /usr/local/bin/taco-system restart'),
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

default_profile_uid = '07139e62-d244-11e0-b94b-00199991c246'
default_profile_config = ('Default', [
    vsplit(
        hsplit(
            panel('nicos.gui.panels.status.ScriptStatusPanel'),
            panel('nicos.gui.panels.watch.WatchPanel')),
        panel('nicos.gui.panels.console.ConsolePanel'),
        ),
    window('Setup', 'setup', True,
           panel('nicos.gui.panels.setup.SetupPanel')),
    window('Editor', 'editor', False,
           panel('nicos.gui.panels.editor.EditorPanel',
                 tools = [
                     tool('Scan', 'nicos.gui.tools.scan.ScanTool')
                 ])),
    window('Live data', 'live', True,
           panel('nicos.mira.gui.live.LiveDataPanel')),
    window('Scans', 'plotter', True,
           panel('nicos.gui.panels.scans.ScansPanel')),
    window('History', 'find', True,
           panel('nicos.gui.panels.history.HistoryPanel')),
    window('Errors', 'errors', True,
           panel('nicos.gui.panels.errors.ErrorPanel')),
    window('Logbook', 'table', True,
           panel('nicos.gui.panels.elog.ELogPanel')),
    ], [
        tool('Maintenance',
             'nicos.gui.tools.commands.CommandsTool',
             commands=maint_commands),
        tool('Calculator',
             'nicos.gui.tools.calculator.CalculatorTool',
             mieze=MIEZE_settings),
        tool('Neutron cross-sections',
             'nicos.gui.tools.website.WebsiteTool',
             url='http://www.ncnr.nist.gov/resources/n-lengths/'),
        tool('Neutron activation',
             'nicos.gui.tools.website.WebsiteTool',
             url='http://www.wise-uranium.org/rnac.html'),
        tool('MIRA Wiki',
             'nicos.gui.tools.website.WebsiteTool',
             url='http://mira2.mira.frm2:8080/'),
        tool('Phone database',
             'nicos.gui.tools.website.WebsiteTool',
             url='http://www.frm2.tum.de/intern/funktionen/phonedb/index.html'),
    ]
)
