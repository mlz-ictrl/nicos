"""NICOS GUI default configuration."""

main_window = docked(
    vsplit(
        panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
        # panel('nicos.clients.gui.panels.watch.WatchPanel'),
        panel('nicos.clients.gui.panels.console.ConsolePanel'),
    ),
    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True,
           show_target=True, dockpos='right',)
    ),
    ('Experiment Information and Setup',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',)
    ),
)

windows = [
    window('Editor', 'editor',
           panel('nicos.clients.gui.panels.editor.EditorPanel')),
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
]

tools = [
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Neutron cross-sections',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Emergency stop button',
         'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=False),
]

options = {
    'connection_presets': {
        'ANTARES': 'antareshw.antares.frm2.tum.de',
        'STRESSI': 'stressictrl.stressi.frm2.tum.de',
        'PUMA': 'pumahw.puma.frm2.tum.de',
        'SPODI': 'spodictrl.spodi.frm2.tum.de',
        'NECTAR': 'nectarhw.nectar.frm2.tum.de',
        'MIRA': 'miractrl.mira.frm2.tum.de',
        'PGAA': 'pgaahw.pgaa.frm2.tum.de',
        'SANS1': 'sans1ctrl.sans1.frm2.tum.de',
        'RESEDA': 'resedactrl.reseda.frm2.tum.de',
        'REFSANS': 'refsansctrl.refsans.frm2.tum.de',
        'TOFTOF': 'tofhw.toftof.frm2.tum.de',
    }
}
