"""NICOS GUI default configuration."""

main_window = tabbed(
    ('Instrument', docked(
        vsplit(
            hsplit(vsplit(
                panel('nicos.clients.gui.panels.cmdbuilder.CommandPanel'),
                panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
            )),
            tabbed(
                ('All output', panel(
                    'nicos.clients.gui.panels.console.ConsolePanel',
                    hasinput=False, hasmenu=False,
                )),
                ('Errors/Warnings', panel(
                    'nicos.clients.gui.panels.errors.ErrorPanel',
                )),
            ),
        ),
        ('Experiment Info', panel(
            'nicos.clients.gui.panels.expinfo.ExpInfoPanel', dockpos='left',
            sample_panel=panel(
                'nicos_jcns.gui.setup_panel.IFFSamplePanel',
            ),
        )),
        ('NICOS devices', panel(
            'nicos.clients.gui.panels.devices.DevicesPanel', icons=True,
            dockpos='right', param_display={
                'pilatus': ['diskspace', 'filename', 'imagedir'],
                'pilatus_config': 'energy',
            },
        )),
    )),
    ('Script Editor', vsplit(
        panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
        panel('nicos.clients.gui.panels.editor.EditorPanel', tools = [
            tool('Scan Generator', 'nicos.clients.gui.tools.scan.ScanTool')
        ]),
    )),
    ('Live data', panel('nicos.clients.gui.panels.live.LiveDataPanel')),
    ('Scan Plotting', panel('nicos.clients.gui.panels.scans.ScansPanel')),
    ('Device Plotting', panel(
        'nicos.clients.gui.panels.history.HistoryPanel'
    )),
    ('Logbook', panel('nicos.clients.gui.panels.elog.ELogPanel')),
)

windows = []

tools = [
    cmdtool('Server control (Marche)', 'marche-gui'),
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool(
        'Neutron cross-sections',
        'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/',
    ),
    tool(
        'Report NICOS bug or request enhancement',
        'nicos.clients.gui.tools.bugreport.BugreportTool',
    ),
    tool(
        'Emergency stop button',
        'nicos.clients.gui.tools.estop.EmergencyStopTool',
        runatstartup=True,
    ),
]
