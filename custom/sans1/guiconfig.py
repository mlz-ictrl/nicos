"""SANS1 GUI default configuration."""

# evaluated by code in: nicos.clients.gui.panels.__init__.createWindowItem

# vsplit( content1, content2, ... )
# hsplit( content1, content2, ... )
# tapped( (tabname1, content1), (tabname2, content2),... )
# docked( content1, (tabname, content2), ... )
## if with tabname, content panels can be stacked, then a tabbar is displayed with the tabnames..

# window( <Button/WindowName>, <icon-name>, bool, content )
# icons are defined in resources/nicos-gui.qrc
## known icons: setup, editor, plotter, find, table, errors, live

# tool( Menu-entry-str, <modulepath>, [, kwargs ] )
## options for all: runatstartup=True/False
## known <modulepaths> below nicos.clients.gui.tools:
# 'nicos.clients.gui.tools.calculator.CalculatorTool'
# 'nicos.clients.gui.tools.website.WebsiteTool'
# 'nicos.clients.gui.tools.estop.EmergencyStopTool'
# 'nicos.clients.gui.tools.scan.ScanTool'
# 'nicos.clients.gui.tools.commands.CommandsTool'

# panel( <modulepath> [, kwargs ] )
## known <modulepath> below nicos.clients.gui.panels:
# 'nicos.clients.gui.panels.cmdbuilder.CommandPanel'
# 'nicos.clients.gui.panels.commandline.CommandLinePanel'
# 'nicos.clients.gui.panels.console.ConsolePanel'
# 'nicos.clients.gui.panels.devices.DevicesPanel' icons = True/False: Show/hide status icons
# 'nicos.clients.gui.panels.editor.EditorPanel'
# 'nicos.clients.gui.panels.elog.ELogPanel'
# 'nicos.clients.gui.panels.errors.ErrorPanel'
# 'nicos.clients.gui.panels.expinfo.ExpInfoPanel'
# loads an uifile='path-to-uifile.ui' from dir='directory-containing-ui-file', also connects to cache ...
# 'nicos.clients.gui.panels.generic.GenericPanel'
# 'nicos.clients.gui.panels.history.HistoryPanel'
# 'nicos.clients.gui.panels.live.LiveDataPanel'
# 'nicos.clients.gui.panels.logviewer.LogViewerPanel'
# 'nicos.clients.gui.panels.scans.ScansPanel'
# 'nicos.clients.gui.panels.scriptbuilder.CommandsPanel'
# 'nicos.clients.gui.panels.setup_panel.SetupPanel'
# 'nicos.clients.gui.panels.status.ScriptStatusPanel'
# 'nicos.clients.gui.panels.watch.WatchPanel'


main_window = docked(
    vsplit(
        panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
        # panel('watch.WatchPanel'),
        panel('nicos.clients.gui.panels.console.ConsolePanel',
              watermark='/sans1control/custom/sans1/watermark.png'),
    ),
    # ('Watch Expressions',panel('watch.WatchPanel')),
    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True,
           dockpos='right',)
    ),
    ('Experiment info',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel')),
)

windows = [
    window('Setup', 'setup',
           tabbed(
               ('Experiment',
                panel('nicos.clients.gui.panels.setup_panel.ExpPanel')),
               ('Setups',
                panel('nicos.clients.gui.panels.setup_panel.SetupsPanel')),
               ('Detectors/Environment',
                panel('nicos.clients.gui.panels.setup_panel.DetEnvPanel')),
               ('Samples',
                panel('nicos_mlz.sans1.gui.samplechanger.SamplechangerSetupPanel',
                      # image='custom/sans1/lib/gui/sampleChanger11.png',
                      image='custom/sans1/lib/gui/sampleChanger22.png',
                      # positions = 11, setups='!setup22',)),
                      positions = 22, setups=['sc1', 'sc2', 'ccmsanssc'],),
               ),
           )
    ),
    window('Editor', 'editor',
           vsplit(
               panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
               panel('nicos.clients.gui.panels.editor.EditorPanel',
                     tools = [
                         tool('Scan',
                              'nicos.clients.gui.tools.scan.ScanTool')
                     ]
               )
           )
    ),
    window('Watches', 'leds/blue_on',
           panel('nicos.clients.gui.panels.watch.WatchPanel')),
    window('Scans', 'plotter',
           panel('nicos.clients.gui.panels.scans.ScansPanel')),
    window('History', 'find',
           panel('nicos.clients.gui.panels.history.HistoryPanel')),
    window('Logbook', 'table',
           panel('nicos.clients.gui.panels.elog.ELogPanel')),
    window('Log files', 'table',
           panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
    window('Errors', 'errors',
           panel('nicos.clients.gui.panels.errors.ErrorPanel')),
    window('Camera', 'live',
           panel('nicos.clients.gui.panels.liveqwt.LiveDataPanel',
                 instrument='poli')),
]

tools = [
    tool('Downtime report',
         'nicos.clients.gui.tools.downtime.DownTimeTool',
         receiver='f.carsughi@fz-juelich.de',
         mailserver='smtp.frm2.tum.de',
         sender='sans1@frm2.tum.de',
    ),
    tool('Calculator',
         'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Neutron cross-sections',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Emergency stop button',
         'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=False),
    tool('Maintenance commands',
         'nicos.clients.gui.tools.commands.CommandsTool',
         commands=[
             ('TACO server control panel (beta)',
              'SSH_ASKPASS=/usr/bin/ssh-askpass setsid /usr/bin/ssh -XY '
              'maint@sans1hw.sans1.frm2 "source /etc/tacoenv.sh && '
              'sudo /usr/bin/python /opt/tacocp/tacocp.py '
              'sans1srv.sans1.frm2" && exit',
             ),
         ]),
]
