"""NICOS GUI default configuration."""

main_window = docked(
   tabbed(
        ('PGAA',
         panel('nicos_mlz.pgaa.gui.panels.PGAAPanel', setups='pgaa',)
        ),
        ('Tomography',
         panel('nicos_mlz.pgaa.gui.panels.TomographyPanel', setups='tomography',),
        ),
        ('Shutter/Attenuators',
         panel('nicos.clients.gui.panels.generic.GenericPanel',
               uifile='nicos_mlz/pgaa/gui/shutter.ui'),
        ),
        ('Expert mode',
         vsplit(
            panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
            # panel('nicos.clients.gui.panels.watch.WatchPanel'),
            panel('nicos.clients.gui.panels.console.ConsolePanel'),
         ),
        ),
    ),
    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True,
           dockpos='right',)
    ),
    ('Experiment Information and Setup',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',
           sample_panel=panel(# 'Sample changer',
                              'nicos_mlz.sans1.gui.samplechanger.SamplechangerSetupPanel',
                              # image='nicos_mlz/sans1/gui/sampleChanger22.png',
                              positions=16, setups='pgaa'),
          ),
    ),
)

windows = [
    window('Editor', 'editor',
           panel('nicos.clients.gui.panels.editor.EditorPanel')),
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
]

tools = [
    tool('Downtime report', 'nicos.clients.gui.tools.downtime.DownTimeTool',
         receiver='f.carsughi@fz-juelich.de',
         mailserver='smtp.frm2.tum.de',
         sender='pgaa@frm2.tum.de',
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
