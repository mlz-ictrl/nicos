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
            ('RT-9.5m 2x9-pos.',                  (9,  2, 'sam_x', 27,   'sam_y', 78)),
            ('RT-1.3m 2x9-pos.',                  (9,  2, 'sam_x', 27,   'sam_y', 75)),
            ('RT-9.5m 2x12-pos. Narrow',          (12,  2, 'sam_x', 20,   'sam_y', 78)),
            ('RT-1.3m 2x12-pos. Narrow',          (12,  2, 'sam_x', 20,   'sam_y', 75)),
            ('Peltier-Old 1x6',                   (6,  1, 'sam_x', 36.6, 'sam_y', 10)),
            ('Cells-in-Vacuum (Julabo) 2x4-pos.', (4,  2, 'sam_x', 24,   'sam_y', 65)),
                                     ]))),
        ('NICOS devices',
            panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True, dockpos='right',
            param_display={'Exp': ['lastpoint']})),
    )),
    ('Script Editor',
        vsplit(
            panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
            panel('nicos.clients.gui.panels.editor.EditorPanel'),
        )),
    ('Scan Plotting', panel('nicos.clients.gui.panels.scans.ScansPanel')),
    ('Device Plotting', panel('nicos.clients.gui.panels.history.HistoryPanel')),
    ('Protocol', panel('nicos_mlz.kws1.gui.protocol.ProtocolPanel')),
)

windows = []

tools = [
    cmdtool('Detector live view', 'KWSlive'),
    cmdtool('Server control (Marche)', 'marche-gui'),
#    cmdtool('NICOS status', 'nicos-monitor'),
    tool('Sample environment logbooks',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://wiki.frm2.tum.de/se:jcns:log:index'),
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
         sender='kws3@frm2.tum.de'),
]
