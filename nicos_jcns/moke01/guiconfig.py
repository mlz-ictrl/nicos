"""NICOS GUI configuration for MOKE."""

main_window = tabbed(
    ('Instrument',
        docked(
            vsplit(
                hsplit(
                    vsplit(
                        panel('nicos.clients.gui.panels.cmdbuilder.CommandPanel'),
                        panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
                    ),
                ),
                tabbed(
                    ('All output',
                        panel('nicos.clients.gui.panels.console.ConsolePanel',
                              hasinput=False, hasmenu=False)),
                    ('Errors/Warnings',
                        panel('nicos.clients.gui.panels.errors.ErrorPanel')),
                ),
            ),
            ('Experiment Info',
                panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel', dockpos='left'),
            ),
            ('NICOS devices',
                panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True, dockpos='right')),
        )
    ),
    ('Script Editor',
        vsplit(
            panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
            panel('nicos.clients.gui.panels.editor.EditorPanel'),
        )
     ),
    ('Scan Plotting', panel('nicos.clients.gui.panels.scans.ScansPanel')),
    ('Device Plotting', panel('nicos.clients.gui.panels.history.HistoryPanel')),
    ('MOKE',
        vsplit(
            panel('nicos_jcns.moke01.gui.moke.MokePanel'),
            setups='moke',
        ),
    ),
    ('Measurement history',
        vsplit(
            panel('nicos_jcns.moke01.gui.moke.MokeHistory'),
            setups='moke',
        ),
    ),
)

windows = []

tools = [
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Emergency stop button', 'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=True),
]
