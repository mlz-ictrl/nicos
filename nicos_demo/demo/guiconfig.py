"""NICOS GUI default configuration."""

main_window = docked(
    tabbed(
        ('Command line',
         vsplit(
            panel('nicos.clients.gui.panels.cmdbuilder.CommandPanel',
                  modules=['nicos.clients.gui.cmdlets'],
            ),
            panel('nicos.clients.gui.panels.status.ScriptStatusPanel', eta=True),
            panel('nicos.clients.gui.panels.console.ConsolePanel',
                  watermark='nicos_demo/demo/gui/nicos-watermark.png', hasinput=False),
         ),
        ),
        ('SANS',
         vsplit(
          panel('nicos_demo.demo.gui.sanspanel.SANSPanel'),
          panel('nicos.clients.gui.panels.live.LiveDataPanel'),
          setups='sans',
         ),
        ),
    ),
    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel',
           dockpos='right',
           param_display={'tas': 'scanmode',
                          'Exp': ['lastpoint', 'lastscan']},
           filters=[('Detector', 'det'),
                    ('Temperatures', '^T'),
                   ],
          )
    ),
    ('Experiment Information and Setup',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',
           sample_panel=tabbed(
               ('Sample changer',
                panel('nicos_mlz.sans1.gui.samplechanger.SamplechangerSetupPanel',
                      image='nicos_mlz/sans1/gui/sampleChanger11.png',
                      positions=11, setups='sans and sc1',),
               ),
               ('Sample changer',
                panel('nicos_mlz.sans1.gui.samplechanger.SamplechangerSetupPanel',
                      image='nicos_mlz/sans1/gui/sampleChanger22.png',
                      positions=22, setups='sans and sc2'),
               ),
               ('TAS sample',
                panel('nicos.clients.gui.panels.setup_panel.TasSamplePanel',
                      setups='tas',)
               ),
               ('SXTAL sample',
                panel('nicos.clients.gui.panels.setup_panel.SXTalSamplePanel',
                      setups='sxtal',)
               ),
           ),
           # to configure panels to show on New/FinishExperiment
           # new_exp_panel=panel('nicos_demo.demo.some.panel'),
           # finish_exp_panel=panel('nicos_demo.demo.some.panel'),
          )
    ),
)

windows = [
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
    window('Live data', 'live',
           panel('nicos.clients.gui.panels.live.LiveDataPanel')),
    window('Logbook', 'table',
           panel('nicos.clients.gui.panels.elog.ELogPanel')),
    window('Log files', 'table',
           panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
    window('Errors', 'errors',
           panel('nicos.clients.gui.panels.errors.ErrorPanel')),
    window('Watchdog', 'errors',
           panel('nicos.clients.gui.panels.watchdog.WatchdogPanel')),
]

tools = [
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
