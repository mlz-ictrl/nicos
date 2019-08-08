"""NICOS GUI default configuration."""

main_window = docked(
    tabbed(
        ('Setup',
         tabbed(
             ('Experiment',
              panel('nicos.clients.gui.panels.setup_panel.ExpPanel')),
             ('Samples',
              panel(
                  'nicos_mlz.kws1.gui.sampleconf.KWSSamplePanel',
                  image='nicos_mlz/sans1/gui/sampleChanger22.png',
                  positions=22, setups='sans and sc2')
              ),
             ('Instrument',
              panel('nicos.clients.gui.panels.setup_panel.SetupsPanel')),
         ),
        ),
        ('  ', panel('nicos_ess.gui.panels.empty.EmptyPanel')),
        ('Instrument interaction',
         hbox(
             vbox(
                 panel(
                     'nicos.clients.gui.panels.cmdbuilder.CommandPanel',
                      modules=['nicos.clients.gui.cmdlets'],
                    ),
                 tabbed(
                     ('Output',
                      panel('nicos.clients.gui.panels.console.ConsolePanel',
                            hasinput=False)),
                     ('Scan Plot',
                      panel('nicos.clients.gui.panels.scans.ScansPanel')),
                     ('Detector Image',
                      panel('nicos.clients.gui.panels.live.LiveDataPanel')),
          		     ('Script Status',
        		      panel('nicos.clients.gui.panels.status.ScriptStatusPanel',
		              eta=True)),

                 ),

             ), # vsplit
             panel(
                 'nicos.clients.gui.panels.devices.DevicesPanel',
                 dockpos='right',
                 param_display={'tas': 'scanmode',
                                'Exp': ['lastpoint', 'lastscan']},
                 filters=[('Detector', 'det'),
                          ('Temperatures', '^T'),
                          ],
             ),
         ),  # hsplit
         ),
        (
            'Batch file generation',
            vsplit(
                panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
                panel('nicos.clients.gui.panels.editor.EditorPanel',
                      tools=None),
            ), # vsplit
        ),
        (
            'Experiment status',
            tabbed(
                ('Detector Image',
                 panel('nicos.clients.gui.panels.live.LiveDataPanel')),
                ('Instrument Log',
                 panel('nicos.clients.gui.panels.logviewer.LogViewerPanel',
                       hasinput=False)),
            ),

        ),
        # (
        #     'Sample environment',
        #     panel('nicos.clients.gui.panels.generic.GenericPanel', uifile='nicos_mlz/pgaa/gui/shutter.ui'),
        # ),
        (
            'History',
            panel('nicos.clients.gui.panels.history.HistoryPanel'),
        ),

        position='left',
    ), # tabbed
    #        # to configure panels to show on New/FinishExperiment
    #        # new_exp_panel=panel('nicos_demo.demo.some.panel'),
    #        # finish_exp_panel=panel('nicos_demo.demo.some.panel'),
    #       )
    # ),
)

windows = [
    # window('Setup', 'setup',
    #     tabbed(
    #         ('Experiment',
    #          panel('nicos.clients.gui.panels.setup_panel.ExpPanel')),
    #         ('Setups',
    #          panel('nicos.clients.gui.panels.setup_panel.SetupsPanel')),
    #         ('Detectors/Environment',
    #          panel('nicos.clients.gui.panels.setup_panel.DetEnvPanel')),
    #         ('Samples',
    #             panel('nicos_mlz.sans1.gui.samplechanger.SamplechangerSetupPanel',
    #                   image='nicos_mlz/sans1/gui/sampleChanger22.png',
    #                   positions=22, setups='sans and sc2')
    #         ),
    #         ('Samples',
    #             panel('nicos_mlz.sans1.gui.samplechanger.SamplechangerSetupPanel',
    #                   image='nicos_mlz/sans1/gui/sampleChanger11.png',
    #                   positions=11, setups='sans and sc1')
    #         ),
    #     ),
    # ),
    # window('Editor', 'editor',
    #     vsplit(
    #         panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
    #         panel('nicos.clients.gui.panels.editor.EditorPanel',
    #           tools = [
    #               tool('Scan Generator',
    #                    'nicos.clients.gui.tools.scan.ScanTool')
    #           ]))),
    # window('Scans', 'plotter',
    #        panel('nicos.clients.gui.panels.scans.ScansPanel')),
    # window('History', 'find',
    #        panel('nicos.clients.gui.panels.history.HistoryPanel')),
    # window('Logbook', 'table',
    #        panel('nicos.clients.gui.panels.elog.ELogPanel')),
    # window('Log files', 'table',
    #        panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
    # window('Errors', 'errors',
    #        panel('nicos.clients.gui.panels.errors.ErrorPanel')),
    # window('Live data', 'live',
    #        panel('nicos.clients.gui.panels.live.LiveDataPanel')),
]

tools = [
    # tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    # menu('Neutron helpers',
    #      tool('Neutron cross-sections',
    #           'nicos.clients.gui.tools.website.WebsiteTool',
    #           url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    #      tool('Neutron activation',
    #           'nicos.clients.gui.tools.website.WebsiteTool',
    #           url='https://webapps.frm2.tum.de/intranet/activation/'),
    #      tool('Neutron calculations',
    #           'nicos.clients.gui.tools.website.WebsiteTool',
    #           url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    # ),
    # tool('Report NICOS bug or request enhancement',
    #      'nicos.clients.gui.tools.bugreport.BugreportTool'),
    # tool('Emergency stop button',
    #      'nicos.clients.gui.tools.estop.EmergencyStopTool',
    #      runatstartup=False),
]
