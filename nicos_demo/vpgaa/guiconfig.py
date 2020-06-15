"""NICOS GUI default configuration."""

main_window = docked(
   tabbed(
        ('PGAA',
         panel('nicos_mlz.pgaa.gui.panels.PGAAPanel', setups='pgaa',)
        ),
        ('Tomography',
         panel('nicos_mlz.pgaa.gui.panels.TomographyPanel', setups='tomography',),
        ),
        ('PGAI',
         panel('nicos_mlz.pgaa.gui.panels.PGAIPanel', setups='pgai',)
        ),
        ('Expert mode',
         vsplit(
            panel('nicos.clients.gui.panels.status.ScriptStatusPanel', eta=True),
            # panel('nicos.clients.gui.panels.watch.WatchPanel'),
            panel('nicos.clients.gui.panels.console.ConsolePanel'),
         ),
        ),
        ('Shutter/Attenuators',
         panel('nicos.clients.gui.panels.generic.GenericPanel',
               uifile='nicos_mlz/pgaa/gui/shutter.ui', setups='not pgaa'),
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
           panel('nicos.clients.gui.panels.scans.ScansPanel'),
           setups='not tomo and not pgaa and not pgai'),
    window('History', 'find',
           panel('nicos.clients.gui.panels.history.HistoryPanel')),
    window('Logbook', 'table',
           panel('nicos.clients.gui.panels.elog.ELogPanel')),
    window('Log files', 'table',
           panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
    window('Errors', 'errors',
           panel('nicos.clients.gui.panels.errors.ErrorPanel')),
    window('Live data', 'live',
           panel('nicos.clients.gui.panels.liveqwt.LiveDataPanel',
                 instrument = 'imaging'), setups='tomo'),
    window('Live data', 'live',
           panel('nicos_mlz.pgaa.gui.panels.live.LiveDataPanel'),
           setups='not tomo'),
]

tools = [
    tool('Downtime report', 'nicos.clients.gui.tools.downtime.DownTimeTool',
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
