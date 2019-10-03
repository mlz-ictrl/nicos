"""NICOS GUI default configuration."""

main_window = docked(
    tabbed(
        ('Setup',
         tabbed(
             ('Experiment',
              panel('nicos_ess.gui.panels.setup_panel.ExpPanel')),
             ('Samples',
              panel(
                  'nicos_mlz.kws1.gui.sampleconf.KWSSamplePanel',
                  image='nicos_mlz/sans1/gui/sampleChanger22.png',
                  positions=22, setups='sans and sc2')
              ),
             ('Instrument',
              panel('nicos_ess.gui.panels.setup_panel.SetupsPanel')),
         ),
        ),
        ('  ', panel('nicos_ess.gui.panels.empty.EmptyPanel')),
        ('Instrument interaction',
         hbox(
             vbox(
                 panel(
                     'nicos_ess.gui.panels.cmdbuilder.CommandPanel',
                      modules=['nicos.clients.gui.cmdlets'],
                    ),
                 tabbed(
                     ('Output',
                      panel('nicos_ess.gui.panels.console.ConsolePanel',
                            hasinput=False,
                            reverse_scrolling=True)),
                     ('Scan Plot',
                      panel('nicos_ess.gui.panels.scans.ScansPanel')),
                     ('Detector Image',
                      panel('nicos_ess.gui.panels.live.LiveDataPanel')),
                     ('Script Status',
                      panel('nicos_ess.gui.panels.status.ScriptStatusPanel', 
                            eta=True)),
                 ),

             ), # vsplit
             panel(
                 'nicos_ess.gui.panels.devices.DevicesPanel',
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
                panel('nicos_ess.gui.panels.editor.EditorPanel',
                      tools=None),
            ), # vsplit
        ),
        (
            'History',
            panel('nicos_ess.gui.panels.history.HistoryPanel'),
        ),

        ('  ', panel('nicos_ess.gui.panels.empty.EmptyPanel')),

        ('Finish Experiment',
         panel('nicos_ess.gui.panels.setup_panel.FinishPanel')),

        position='left',
    ), # tabbed

    ) #docked

windows = [ ]

tools = [
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
]

options = {
    'ess_gui' : True,
}
