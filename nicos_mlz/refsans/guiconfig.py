"""NICOS GUI default configuration."""

chopper_params = ['current', 'phase', 'mode']

main_window = docked(
    vsplit(
        panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
        # panel('watch.WatchPanel'),
        panel('nicos.clients.gui.panels.console.ConsolePanel'),
    ),
    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True,
           dockpos='right',
           param_display={
               'chopper': ['mode', 'wlmin', 'wlmax'],
               'chopper_speed': ['current', 'mode'],
               'chopper2': chopper_params + ['pos'],
               'chopper3': chopper_params,
               'chopper4': chopper_params,
               'chopper5': chopper_params,
               'chopper6': chopper_params,
               'nok9': 'mode',
               'nok8': 'mode',
               'nok7': 'mode',
               'nok6': 'mode',
               'nok5b': 'mode',
               'nok5a': 'mode',
               'nok4': 'mode',
               'nok3': 'mode',
               'nok2': 'mode',
               'b1': 'mode',
               'b2': 'mode',
               'b3': 'mode',
               'bs1': 'mode',
               'zb0': 'mode',
               'zb1': 'mode',
               'zb2': 'mode',
               'zb3': 'mode',
               },
           ),
    ),
    ('Experiment Information and Setup',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',),
    ),
)

windows = [
    window('Live data', 'live',
           panel('nicos.clients.gui.panels.live.LiveDataPanel')),
    window('Editor', 'editor',
       vsplit(
           panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
           panel('nicos.clients.gui.panels.editor.EditorPanel',
           ))),
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
    window('Watchdog', 'errors',
           panel('nicos.clients.gui.panels.watchdog.WatchdogPanel')),
    window('Planning', 'strategy',
           panel('nicos_mlz.refsans.gui.resolutionpanel.ResolutionPanel')),
]

tools = [
    tool('Downtime report', 'nicos.clients.gui.tools.downtime.DownTimeTool',
         sender='refsans@frm2.tum.de',
        ),
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Neutron cross-sections',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Emergency stop button',
         'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=False),
]
