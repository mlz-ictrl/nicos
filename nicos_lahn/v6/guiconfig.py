"""NICOS GUI default configuration."""

main_window = docked(
    tabbed(
        ('Command Line',
         vsplit(
             panel('nicos.clients.gui.panels.cmdbuilder.CommandPanel',
                   modules=['nicos.clients.gui.cmdlets'],
                   ),
             panel('nicos.clients.gui.panels.status.ScriptStatusPanel', eta=True),
             panel('nicos.clients.gui.panels.console.ConsolePanel',
                   hasinput=False),
         ),
         ),
        ('Instrument',
         panel('nicos_lahn.v6.gui.rnppanel_1.RNPPanel',
               setups='RN or RNOS or RNP or RNPOS'),
         ),
        ('Instrument',
         panel('nicos_lahn.v6.gui.rnppanel_2.RNPPanel',
               setups='RNL or RNLOS'),
         ),
        ('Sample Environment',
         panel('nicos_lahn.v6.gui.sample_environment.Sample_Environment',
               setups='sample_environment'),
         ),
        ('Polarization',
         panel('nicos_lahn.v6.gui.polarization_1.Polarization',
               setups='RNP'),
         ),
        ('Polarization',
         panel('nicos_lahn.v6.gui.polarization_2.Polarization',
               setups='RNPOS'),
         ),
    ),
    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True,
           dockpos='right'),
     ),
    ('Experiment Information and Setup',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel'),
     ),
)

windows = [
    window('Editor', 'editor',
           vsplit(
               panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
               panel('nicos.clients.gui.panels.editor.EditorPanel',
                     ))),
    window('Scans', 'plotter',
           panel('nicos.clients.gui.panels.scans.ScansPanel')),
    window('History', 'find',
           panel('nicos.clients.gui.panels.history.HistoryPanel')),
    window('Live data', 'live',
           panel('nicos.clients.gui.panels.live.LiveDataPanel')),
    window('Logbook', 'table',
           panel('nicos.clients.gui.panels.elog.ELogPanel')),
    window('Log files', 'table',
           panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
    window('Errors', 'errors',
           panel('nicos.clients.gui.panels.errors.ErrorPanel')),
]

tools = [
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Neutron cross-sections',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Emergency stop button',
         'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=False),
]

options = {
    'facility_logo': ':/lahn/lahn-logo-auth',
}
