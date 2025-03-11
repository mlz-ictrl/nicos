"""NICOS GUI default configuration."""

main_window = docked(
    tabbed(
        ('Experiment info',
            panel('nicos_mgml.gui.panels.setup_panel.ExpPanel'),
        ),
        ('Command line',
         vsplit(
            panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
            panel('nicos.clients.gui.panels.console.ConsolePanel'),
         ),
        ),
       #('Logbook', panel('nicos.clients.gui.panels.elog.ELogPanel')),
       #('Log files', panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
       #('Errors', panel('nicos.clients.gui.panels.errors.ErrorPanel')),
       #('Watchdog', panel('nicos.clients.gui.panels.watchdog.WatchdogPanel')),
    ),
    ('Information',
       vsplit(
        panel('nicos_mgml.gui.panels.utils.ImagePanel',
              image='nicos_mgml/resources/logo.png'),
        panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',
                    ),
    ),)
)

windows = [ ]

tools = [
]

options = {
    'mainwindow_class': 'nicos_mgml.gui.mainwindow.MainWindow',
}
