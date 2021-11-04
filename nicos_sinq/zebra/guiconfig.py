#  -*- coding: utf-8 -*-
"""NICOS GUI default configuration."""

main_window = tabbed(
    (
        'Instrument',
        docked(
            vsplit(
                tabbed(
                    (
                        'All output',
                        panel(
                            'nicos.clients.gui.panels.console.ConsolePanel',
                            hasinput = True,
                            hasmenu = True,
                            watermark = 'nicos_sinq/watermark.png'
                        )
                    ),
                    (
                        'Errors/Warnings',
                        panel('nicos.clients.gui.panels.errors.ErrorPanel')
                    ),
                ),
            ),
            (
                'Experiment Setup',
                panel(
                    'nicos.clients.gui.panels.expinfo.ExpInfoPanel',
                    dockpos = 'left'
                )
            ),
            (
                'Control devices',
                panel(
                    'nicos.clients.gui.panels.devices.DevicesPanel',
                    icons = True,
                    dockpos = 'right'
                )
            ),
        )
    ),
    (
        'Script Builder',
        vsplit(
            panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
            panel(
                'nicos.clients.gui.panels.editor.EditorPanel',
                tools = [
                    tool(
                        'Scan Generator',
                        'nicos.clients.gui.tools.scan.ScanTool'
                    )
                ]
            ),
        )
    ),
    ('Device History', panel('nicos.clients.gui.panels.history.HistoryPanel')),
    ('Log files', panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
)

windows = [
    window(
        'Editor', 'editor',
        panel('nicos.clients.gui.panels.editor.EditorPanel')
    ),
    window(
        'Scans', 'plotter', panel('nicos.clients.gui.panels.scans.ScansPanel')
    ),
    window(
        'Logbook', 'table', panel('nicos.clients.gui.panels.elog.ELogPanel')
    ),
    window(
        'LiveData', 'livedata',
        panel('nicos_sinq.gui.powderlive.LivePowderPanel', sttstep = 0.1)
    ),
]

tools = [
    tool(
        'Emergency stop button',
        'nicos.clients.gui.tools.estop.EmergencyStopTool',
        runatstartup = False
    ),
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool(
        'Neutron cross-sections',
        'nicos.clients.gui.tools.website.WebsiteTool',
        url = 'http://www.ncnr.nist.gov/resources/n-lengths/'
    ),
    tool(
        'Neutron activation',
        'nicos.clients.gui.tools.website.WebsiteTool',
        url = 'https://webapps.frm2.tum.de/intranet/activation/'
    ),
    tool(
        'Neutron calculations',
        'nicos.clients.gui.tools.website.WebsiteTool',
        url = 'https://webapps.frm2.tum.de/intranet/neutroncalc/'
    ),
    tool(
        'Report NICOS bug or request enhancement',
        'nicos.clients.gui.tools.bugreport.BugreportTool'
    ),
]
