"""SANS1 GUI default configuration."""

main_window = docked(
    vsplit(
        panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
        # panel('watch.WatchPanel'),
        panel('nicos.clients.gui.panels.console.ConsolePanel',
              watermark='nicos_mlz/sans1/gui/watermark.png'),
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
                      # image='nicos_mlz/sans1/gui/sampleChanger11.png',
                      image='nicos_mlz/sans1/gui/sampleChanger22.png',
                      # positions = 11, setups='not setup22',)),
                      positions = 22, setups='sc? or ccmsanssc',),
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
