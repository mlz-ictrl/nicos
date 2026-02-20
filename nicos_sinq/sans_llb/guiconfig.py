"""NICOS GUI default configuration."""

main_window = docked(
    tabbed(
        ('Setup',
         tabbed(
             ('Experiment',
              panel('nicos_sinq.gui.panels.setup_panel.ExpPanel')),
             ('Instrument',
              panel('nicos.clients.flowui.panels.setup_panel.SetupsPanel')),
         ),
        ),
        (
            'Sample Changer',
            vsplit(
                panel('nicos_sinq.sans_llb.gui.panels.sample_changer_panel.SampleChangerPanel'),
            ), # vsplit
        ),
        ('  ', panel('nicos.clients.flowui.panels.empty.EmptyPanel')),
        ('Instrument interaction',
         hsplit(
             vbox(
                 panel(
                     'nicos.clients.flowui.panels.cmdbuilder.CommandPanel',
                    ),
                 tabbed(
                     ('Output',
                      panel('nicos.clients.flowui.panels.console.ConsolePanel',
                            hasinput=False)),
                     ('Scan Plot',
                      panel('nicos.clients.flowui.panels.scans.ScansPanel')),
                     ('Detector Image',
                      panel('nicos.clients.flowui.panels.live.LiveDataPanel')),
                     ('Script Status',
                      panel('nicos.clients.flowui.panels.status.ScriptStatusPanel',
                            eta=True)),
                 ),

             ), # vsplit
             panel(
                 'nicos.clients.flowui.panels.devices.DevicesPanel',
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
                panel('nicos.clients.flowui.panels.editor.EditorPanel',
                      tools=None),
            ), # vsplit
        ),
        ('Detector Image', panel('nicos.clients.flowui.panels.live.LiveDataPanel')),
        (
            'History',
            panel('nicos.clients.flowui.panels.history.HistoryPanel'),
        ),
        ('Logs',
            tabbed(
                ('Errors', panel('nicos.clients.gui.panels.errors.ErrorPanel')),
                ('Log files', panel(
                    'nicos.clients.gui.panels.logviewer.LogViewerPanel')),
            ),
         ),


        ('  ', panel('nicos.clients.flowui.panels.empty.EmptyPanel')),

        ('Finish Experiment',
         panel('nicos.clients.flowui.panels.setup_panel.FinishPanel')),

        position='left',
    ), # tabbed

    ) #docked

windows = [ ]

tools = [
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
]

options = {
    'mainwindow_class': 'nicos_sinq.gui.mainwindow.MainWindow',
}
