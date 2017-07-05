"""NICOS GUI default configuration."""

main_window = docked(
    tabbed(
        ('Command line',
         vsplit(
            panel('nicos.clients.gui.panels.status.ScriptStatusPanel',
                  eta=True),
            # panel('nicos.clients.gui.panels.watch.WatchPanel'),
            panel('nicos.clients.gui.panels.console.ConsolePanel',
                  watermark='resources/nicos-watermark.png'),
         ),
        ),
        ('PGAA',
         panel('nicos_mlz.pgaa.gui.panels.PGAAPanel', setups='pgaa'),
        ),
        ('Shutter/Attenuators',
         panel('nicos.clients.gui.panels.generic.GenericPanel',
               # TODO path change
               uifile='custom/pgaa/lib/gui/shutter.ui', setups='pgaa'),
        ),
        ('SampleChanger',
         panel('nicos_mlz.sans1.gui.samplechanger.SamplechangerSetupPanel',
               # TODO path change
               image='custom/sans1/lib/gui/sampleChanger11.png',
               positions=11, setups='sans and sc1'),
        ),
        ('SampleChanger',
         panel('nicos_mlz.sans1.gui.samplechanger.SamplechangerSetupPanel',
               # TODO path change
               image='custom/sans1/lib/gui/sampleChanger22.png',
               positions=22, setups='sans and sc2'),
        ),
        ('PiBox',
         panel('nicos.clients.gui.panels.generic.GenericPanel',
               # TODO path change
               uifile='custom/demo/lib/gui/piface.ui', setups='pibox01',)
        ),
#       ('Setup',
#        tabbed(
#           ('Experiment',
#            panel('nicos.clients.gui.panels.setup_panel.ExpPanel')),
#           ('Setups',
#            panel('nicos.clients.gui.panels.setup_panel.SetupsPanel')),
#           ('Detectors/Environment',
#            panel('nicos.clients.gui.panels.setup_panel.DetEnvPanel')),
#        ),
#        'sans',
#       ),
    ),
    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True,
           dockpos='right',)
    ),
    ('Experiment Information and Setup',
     panel('expinfo.ExpInfoPanel',
           sample_panel=tabbed(
               ('Sample changer',
                panel('nicos_mlz.sans1.gui.samplechanger.SamplechangerSetupPanel',
                      # TODO path change
                      image='custom/sans1/lib/gui/sampleChanger11.png',
                      positions=11, setups='sans and sc1',),
               ),
               ('Sample changer',
                panel('nicos_mlz.sans1.gui.samplechanger.SamplechangerSetupPanel',
                      # TODO path change
                      image='custom/sans1/lib/gui/sampleChanger22.png',
                      positions=22, setups='sans and sc2'),
               ),
               ('TAS sample',
                panel('nicos.clients.gui.panel.setup_panel.TasSamplePanel',
                      setups='tas',)
               ),
           )
          )
    ),
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
                panel('sans1.gui.samplechanger.SamplechangerSetupPanel',
                      # TODO path change
                      image='custom/sans1/lib/gui/sampleChanger22.png',
                      positions=22, setups='sans and sc2')
            ),
            ('Samples',
                panel('sans1.gui.samplechanger.SamplechangerSetupPanel',
                      # TODO path change
                      image='custom/sans1/lib/gui/sampleChanger11.png',
                      positions=11, setups='sans and sc1')
            ),
        ),
    ),
    window('Editor', 'editor',
        vsplit(
            panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
            panel('nicos.clients.gui.panels.editor.EditorPanel',
              tools = [
                  tool('Scan Generator',
                       'nicos.clients.gui.tools.scan.ScanTool')
              ]))),
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
    # window('Downtime', 'mail',
    #        panel('nicos.clients.gui.tools.downtime.DownTimeTool')),
    window('Live data', 'live',
           panel('nicos.clients.gui.panels.live.LiveDataPanel')),
]

tools = [
    tool('Downtime report', 'nicos.clients.gui.tools.downtime.DownTimeTool',
#        receiver='f.carsughi@fz-juelich.de',
         receiver='jens.krueger@frm2.tum.de, enrico.faulhaber@frm2.tum.de',
         mailserver='smtp.frm2.tum.de',
         sender='demo@frm2.tum.de',
        ),
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    menu('Neutron helpers',
         tool('Neutron cross-sections',
              'nicos.clients.gui.tools.website.WebsiteTool',
              url='http://www.ncnr.nist.gov/resources/n-lengths/'),
         tool('Neutron activation',
              'nicos.clients.gui.tools.website.WebsiteTool',
              url='https://webapps.frm2.tum.de/intranet/activation/'),
         tool('Neutron calculations',
              'nicos.clients.gui.tools.website.WebsiteTool',
              url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    ),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Emergency stop button',
         'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=False),
]
