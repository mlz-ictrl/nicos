"""NICOS GUI default configuration."""

main_window = tabbed(
    ('Instrument', docked(
        vsplit(
            panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
            panel('nicos.clients.gui.panels.console.ConsolePanel',),
        ),
        ('Experiment Info', panel('nicos_mgml.gui.panels.setup_panel.ExpInfoPanel', dockpos='right')),
        ('NICOS devices',
            vsplit(
            panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True),
            panel('nicos_mgml.gui.panels.lakeshore.LakeshorePanel',),
            dockpos='right'
            )
        ),
    )),
    ('Script Editor',
        vsplit(
            panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
            panel('nicos.clients.gui.panels.editor.EditorPanel',
                tools = [
                    tool('Scan Generator', 'nicos.clients.gui.tools.scan.ScanTool')
            ]),
        )),
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
]

tools = [
    tool('Downtime report', 'nicos.clients.gui.tools.downtime.DownTimeTool',
         receiver='mgml@mgml.eu',
         mailserver='smtp.frm2.tum.de',
         sender='demo@frm2.tum.de',
        ),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
]
