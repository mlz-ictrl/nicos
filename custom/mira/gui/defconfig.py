# Default MIRA GUI config

from nicos.gui.config import vsplit, hsplit, panel, window, tool

maint_commands = [
    ('Restart TACO server for RS232/mira1',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-rs232 restart'),
    ('Restart TACO server for RS485/mira1',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-rs485 restart'),
    ('Restart TACO server for LakeShore',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-lakeshore340 restart'),
    ('Restart TACO server for Phytron',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-phytronixe restart'),
    ('Restart TACO server for FRM counter',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-frmcounter restart'),
    ('Restart TACO server for ZUPs',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-zup restart'),
    ('Restart TACO server for IPC encoder',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-ipcencoder restart'),

    ('Restart TACO server for RS232/mira4',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-rs232 restart'),
    ('Restart TACO server for network/mira4',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-network restart'),
    ('Restart TACO server for HPE power supplies',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-hpe3631a restart'),
    ('Restart TACO server for NTN (FUG)',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-ntn14000m restart'),
    ('Restart TACO server for Heinzinger',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-heinzingerptn3p restart'),
    ('Restart TACO server for Tektronix',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-tektronixtds restart'),
    ('Restart TACO server for Agilent frequency generators',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-hp33250a restart'),
    ('Restart TACO server for C-Boxes',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-pci2032 restart'),
    ('Restart TACO server for TMCA counter',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-tmca restart'),
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

default_profile_config = ('Default', [
    vsplit(
        hsplit(
            panel('nicos.gui.panels.status.ScriptStatusPanel'),
            panel('nicos.gui.panels.watch.WatchPanel')),
        panel('nicos.gui.panels.console.ConsolePanel'),
        ),
    window('Errors/warnings', 'errors', True,
           panel('nicos.gui.panels.errors.ErrorPanel')),
    window('Editor', 'editor', False,
           panel('nicos.gui.panels.editor.EditorPanel')),
    window('Live data', 'live', True,
           panel('nicos.gui.panels.live.LiveDataPanel')),
    window('Analysis', 'plotter', True,
           panel('nicos.gui.panels.analysis.AnalysisPanel')),
    window('History', 'find', True,
           panel('nicos.gui.panels.history.HistoryPanel')),
    ], [
        tool('nicos.gui.tools.commands.CommandsTool',
             commands=maint_commands),
        tool('nicos.gui.tools.calculator.CalculatorTool',
             mieze=MIEZE_settings),
    ]
)
