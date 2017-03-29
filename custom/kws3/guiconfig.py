"""NICOS GUI default configuration."""

main_window = tabbed(
    ('Instrument', docked(
        vsplit(
            hsplit(
                vsplit(
                    panel('cmdbuilder.CommandPanel',
                          modules=['kws1.gui.cmdlets']),
                    panel('status.ScriptStatusPanel'),
                ),
            ),
            tabbed(
                ('All output',
                    panel('console.ConsolePanel',
                          hasinput=False, hasmenu=False, fulltime=True)),
                ('Errors/Warnings',
                    panel('errors.ErrorPanel')),
            ),
        ),
        ('Experiment Info',
            panel('expinfo.ExpInfoPanel', dockpos='left',
                  sample_panel=panel('kws1.gui.sampleconf.KWSSamplePanel',
                                     holder_info = [
                                     ]))),
        ('NICOS devices',
            panel('devices.DevicesPanel', icons=True, dockpos='right')),
    )),
    ('Script Editor',
        vsplit(
            panel('scriptbuilder.CommandsPanel'),
            panel('editor.EditorPanel'),
        )),
    ('Scan Plotting', panel('scans.ScansPanel')),
    ('Device Plotting', panel('history.HistoryPanel')),
#    ('Protocol', panel('nicos.kws1.gui.protocol.ProtocolPanel')),
)

windows = []

tools = [
    cmdtool('Detector live view', 'KWSlive'),
    cmdtool('Server control (Marche)', 'marche-gui'),
    cmdtool('NICOS status', 'nicos-monitor'),
    tool('Emergency stop button', 'estop.EmergencyStopTool',
         runatstartup=False),
    tool('Calculator', 'calculator.CalculatorTool'),
    tool('Neutron cross-sections', 'website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug or request enhancement', 'bugreport.BugreportTool'),
    tool('Downtime report', 'downtime.DownTimeTool',
         receiver='f.carsughi@fz-juelich.de',
         mailserver='smtp.frm2.tum.de',
         sender='kws3@frm2.tum.de',
        ),
]
