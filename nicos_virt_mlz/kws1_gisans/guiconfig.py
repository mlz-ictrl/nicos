"""NICOS GUI default configuration."""

main_window = tabbed(
    ('Instrument', docked(
        vsplit(
            hsplit(
                vsplit(
                    panel('nicos.clients.gui.panels.cmdbuilder.CommandPanel',
                          modules=['nicos_mlz.kws1.gui.cmdlets']),
                    panel('nicos.clients.gui.panels.status.ScriptStatusPanel',
                          eta=True),
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
                                     holder_info = [
            ('Al 3-level',          (9,  3, 'sam_trans_x', 27,     'sam_trans_y', 75)),
            ('Al 3-level (narrow)', (12, 3, 'sam_trans_x', 20,     'sam_trans_y', 75)),
            ('Cu 3-level',          (9,  3, 'sam_trans_x', 27.125, 'sam_trans_y', 113)),
            ('Cu 3-level (narrow)', (16, 3, 'sam_trans_x', 14.78,  'sam_trans_y', 113)),
            ('Peltier 6',           (6,  1, 'sam_trans_x', 36.56,  'sam_trans_y', 0)),
            ('Peltier 8',           (8,  1, 'sam_trans_x', 36.56,  'sam_trans_y', 0)),
            ('Red oven 4',          (4,  1, 'sam_trans_x', 40,     'sam_trans_y', 0)),
            ('Al 2-level (wide)',   (9,  2, 'sam_trans_x', 26.6,   'sam_trans_y', 105.05)),
            ('Al 2-level (narrow)', (16, 2, 'sam_trans_x', 15.0,   'sam_trans_y', 105.05)),
            ('Magnet',              (5,  1, 'em1_sam_trans', 23,   None, 0)),
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

windows = [
    window('Live data', 'live', panel('nicos.clients.gui.panels.live.LiveDataPanel')),
]

tools = [
    tool('Reconfigure instrument', 'nicos_mlz.kws1.gui.instrconfig.InstrumentConfigTool',
         parts=['shutter', 'selector', 'collimation', 'sample', 'polarizer',
                'chopper', 'detector', 'lenses', 'daq']),
    cmdtool('NICOS status', 'nicos-monitor'),
    tool('Emergency stop button', 'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=False),
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Neutron cross-sections', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
]

options = {
    'reader_classes': ['nicos_mlz.kws1.devices.yamlformat'],
}
