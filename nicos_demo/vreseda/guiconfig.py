"""NICOS GUI default configuration."""

main_window = tabbed(
    ('Instrument', docked(
        vsplit(
            panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
            # panel('nicos.clients.gui.panels.watch.WatchPanel'),
            panel('nicos.clients.gui.panels.console.ConsolePanel',
                  watermark='nicos_mlz/reseda/gui/watermark.png'),
        ),
        ('NICOS devices',
         panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True,
               dockpos='right',)
        ),
        ('Experiment Information and Setup',
         panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',)
        ),
        )
    ),
    ('Tunewave table',
     panel('nicos_mlz.gui.tunewavetable.TunewaveTablePanel',
           tabledev='echotime')
    ),
    ('Mieze display',
     panel('nicos_mlz.reseda.gui.mieze_display.MiezePanel',
           setups='det_cascade',
           columns=3, rows=2, foils=[7, 6, 5, 0, 1, 2])
    ),
    ('Mieze display (Reseda II)',
     panel('nicos_mlz.reseda.gui.mieze_display.MiezePanel',
           setups='det_cascade2',
           columns=4, rows=2, foils=[6, 5, 4, 3, 2, 1, 0])
    ),
)

windows = [
    window('Editor', 'editor',
           panel('nicos.clients.gui.panels.editor.EditorPanel')),
    window('Scans', 'plotter',
           panel('nicos.clients.gui.panels.scans.ScansPanel',
                 fit_functions={
                     'Resonance': (['Vmax = 0.1', 'R = 0.6'], 'Vmax / sqrt(R**2 + (f*L-1/(f*C))**2)'),
                     'Echo': ([], 'y_0 * (1 - pol * cos((pi * (t - x_0)) / (2 * echo2pistep)) *'
                                  'sinc((st * (t - x_1))/(2 * echo2pistep))**2)'),
                 },
                )
          ),
    window('History', 'find',
           panel('nicos.clients.gui.panels.history.HistoryPanel')),
    window('Logbook', 'table',
           panel('nicos.clients.gui.panels.elog.ELogPanel')),
    window('Log files', 'table',
           panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
    window('Errors', 'errors',
           panel('nicos.clients.gui.panels.errors.ErrorPanel')),
    window('Live data', 'live',
           panel('nicos_mlz.mira.gui.live.LiveDataPanel')),
]

tools = [
    tool('Downtime report', 'nicos.clients.gui.tools.downtime.DownTimeTool',
         sender='reseda@frm2.tum.de',
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
