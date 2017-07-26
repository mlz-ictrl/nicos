"""NICOS GUI default configuration."""

main_window = tabbed(
    ('Instrument', docked(
        vsplit(
            hsplit(
                vsplit(
                    panel('nicos.clients.gui.panels.cmdbuilder.CommandPanel',
                          modules=['nicos_mlz.kws3.gui.cmdlets']),
                    panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
                ),
            ),
            tabbed(
                ('All output',
                    panel('nicos.clients.gui.panels.console.ConsolePanel',
                          hasinput=False, hasmenu=False, fulltime=True)),
                ('Errors/Warnings',
                    panel('nicos.clients.gui.panels.errors.ErrorPanel')),
            ),
        ),
        ('Experiment Info',
            panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel', dockpos='left',
                  sample_panel=panel('nicos_mlz.kws1.gui.sampleconf.KWSSamplePanel',
                                     instrument = 'kws3',
                                     holder_info = [
            ('Al 3-level',          (9,  3, 'sam_x', 27,    'sam_y', 75)),
            ('Al 3-level Narrow',   (12, 3, 'sam_x', 20,    'sam_y', 75)),
            ('Al Wide (T-contr.)',  (9,  2, 'sam_x', 26.6,  'sam_y', 105)),
            ('Al Narrow (T-contr.)',(16, 2, 'sam_x', 15,    'sam_y', 105)),
            ('Al Round (T-contr.)', (10, 2, 'sam_x', 24,    'sam_y', 105)),
                                     ]))),
        ('NICOS devices',
            panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True, dockpos='right')),
    )),
    ('Script Editor',
        vsplit(
            panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
            panel('nicos.clients.gui.panels.editor.EditorPanel'),
        )),
    ('Scan Plotting', panel('nicos.clients.gui.panels.scans.ScansPanel')),
    ('Device Plotting', panel('nicos.clients.gui.panels.history.HistoryPanel')),
#    ('Protocol', panel('nicos_mlz.kws1.gui.protocol.ProtocolPanel')),
)

windows = []

tools = [
    cmdtool('Detector live view', 'KWSlive'),
    cmdtool('Server control (Marche)', 'marche-gui'),
#    cmdtool('NICOS status', 'nicos-monitor'),
    tool('Emergency stop button', 'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=False),
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Neutron cross-sections', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Downtime report', 'nicos.clients.gui.tools.downtime.DownTimeTool',
         receiver='f.carsughi@fz-juelich.de',
         mailserver='smtp.frm2.tum.de',
         sender='kws3@frm2.tum.de',
        ),
]
