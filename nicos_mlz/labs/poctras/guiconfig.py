"""NICOS GUI configuration for ANTARES."""

main_window = docked(
    vsplit(
       panel('nicos.clients.gui.panels.cmdbuilder.CommandPanel',
             modules=['nicos.clients.gui.cmdlets.tomo'],
       ),
       panel('nicos.clients.gui.panels.status.ScriptStatusPanel', eta=True),
       panel('nicos.clients.gui.panels.console.ConsolePanel',
             watermark='nicos_demo/demo/gui/nicos-watermark.png', hasinput=False),
    ),
    ('Experiment info',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel')),
    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True,
           dockpos='right',)
    ),
)

windows = [
    window('Setup', 'setup',
           tabbed(('Experiment',
                   panel('nicos.clients.gui.panels.setup_panel.ExpPanel')),
                  ('Setups',
                   panel('nicos.clients.gui.panels.setup_panel.SetupsPanel')),
                  ('Detectors/Environment',
                   panel('nicos.clients.gui.panels.setup_panel.DetEnvPanel')),
            )),
    window('Editor', 'editor',
           vsplit(
               panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
               panel('nicos.clients.gui.panels.editor.EditorPanel'))),
    window('Scans', 'plotter',
           panel('nicos.clients.gui.panels.scans.ScansPanel')),
    window('History', 'find',
           panel('nicos.clients.gui.panels.history.HistoryPanel')),
    window('Logbook', 'table',
           panel('nicos.clients.gui.panels.elog.ELogPanel')),
    window('Errors', 'errors',
           panel('nicos.clients.gui.panels.errors.ErrorPanel')),
    window('Live data', 'live',
           panel('nicos.clients.gui.panels.live.ImagingLiveDataPanel',
                 filetypes=['fits'],)),
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
    # tool('Report NICOS bug or request enhancement',
    #      'nicos.clients.gui.tools.bugreport.BugreportTool'),
]
