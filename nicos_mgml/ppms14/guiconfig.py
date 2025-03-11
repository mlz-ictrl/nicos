"""NICOS GUI default configuration."""

main_window = docked(
    tabbed(
        ('Experiment info',
          vsplit(
            panel('nicos_mgml.gui.panels.setup_panel.ExpPanel'),
            panel('nicos_mgml.gui.panels.utils.CryoPanel'),
          ),
        ),
        ('Command line',
         vsplit(
            panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
            panel('nicos.clients.gui.panels.console.ConsolePanel'),
         ),
        ),
       ('Script Editor',
           panel('nicos.clients.gui.panels.editor.EditorPanel'),
       ),
       ('Logbook', panel('nicos.clients.gui.panels.elog.ELogPanel')),
       ('Log files', panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
       ('Errors', panel('nicos.clients.gui.panels.errors.ErrorPanel')),
       ('Watchdog', panel('nicos.clients.gui.panels.watchdog.WatchdogPanel')),
    ),
    ('Information',
       vsplit(
        panel('nicos_mgml.gui.panels.utils.ImagePanel',
              image='nicos_mgml/resources/logo.png'),
        panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',
                    ),
        panel('nicos.clients.gui.panels.devices.DevicesPanel',
                     param_display={'Exp': ['consumed', 'started', ]},
                     filters=[('Detector', 'det'),
                            ('Temperatures', '^T'),
                            ],
                     ),
    ),)
)

windows = [ ]

tools = [
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
]

options = {
    'mainwindow_class': 'nicos_mgml.gui.mainwindow.MainWindow',
}
