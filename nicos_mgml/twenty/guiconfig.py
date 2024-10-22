"""NICOS GUI default configuration."""

main_window = tabbed(
    ('Instrument', docked(
        vsplit(
            panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
            panel('nicos.clients.gui.panels.console.ConsolePanel',),
        ),
        ('Experiment Info',
            vsplit(
                panel('nicos_mgml.gui.panels.setup_panel.ExpInfoPanel', dockpos='right'),
                panel('nicos_mgml.gui.panels.utils.CryoPanel'),
            )
        ),
        ('NICOS devices',
            vsplit(
                panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True),
                panel('nicos_mgml.gui.panels.lakeshore.LakeshorePanel'),
                dockpos='right'
            )
        ),
    )),
    ('Script Editor',
        vsplit(
            panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
            panel('nicos.clients.gui.panels.editor.EditorPanel'),
        ),
    ),
    ('Scan Plotting', panel('nicos.clients.gui.panels.scans.ScansPanel')),
    ('Device Plotting', panel('nicos.clients.gui.panels.history.HistoryPanel')),
    ('Logbook', panel('nicos.clients.gui.panels.elog.ELogPanel')),
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
        ),
    ),
    window('Editor', 'editor',
        vsplit(
            panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
            panel('nicos.clients.gui.panels.editor.EditorPanel'),
        )),
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
         receiver='mgml@mgml.eu',
         mailserver='smtp.karlov.mff.cuni.cz:465',
         sender='mgml@mgml.eu',
        ),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
]

options = {
    'mainwindow_class': 'nicos_mgml.gui.mainwindow.MainWindow',
}
