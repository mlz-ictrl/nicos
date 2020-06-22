"""NICOS GUI default configuration."""

main_window = docked(
    tabbed(
        ('Script',
         vsplit(
            panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
            panel('nicos.clients.gui.panels.console.ConsolePanel'),
         ),
        ),
    ),
    ('NICOS Devices',
        panel('nicos.clients.gui.panels.devices.DevicesPanel'),
    ),
    ('Experiment Information and Setup',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',
           sample_panel=tabbed(
               ('TAS sample',
                panel('nicos.clients.gui.panels.setup_panel.TasSamplePanel',
                      setups='tas',)
               ),
           ),
           # to configure panels to show on New/FinishExperiment
           # new_exp_panel=panel('nicos_demo.demo.some.panel'),
           # finish_exp_panel=panel('nicos_demo.demo.some.panel'),
     ),
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
                panel('nicos.clients.gui.panels.editor.EditorPanel',
                  tools = [
                      tool('Scan', 'nicos.clients.gui.tools.scan.ScanTool')
                  ]))),
        window('Scans', 'plotter',
            panel('nicos.clients.gui.panels.scans.ScansPanel')),
        window('History', 'find',
            panel('nicos.clients.gui.panels.history.HistoryPanel')),
        window('Logbook', 'table',
            panel('nicos.clients.gui.panels.elog.ELogPanel')),
        window('Errors', 'errors',
            panel('nicos.clients.gui.panels.errors.ErrorPanel')),
        window('Live data', 'live',
            panel('nicos.clients.gui.panels.live.LiveDataPanel')),
        window('TAS status', 'table',
            panel('nicos.clients.gui.panels.generic.GenericPanel',
                  uifile='nicos/clients/gui/panels/tasaxes.ui')),
        window('Polarization analysis', 'polarization',
            panel('nicos_mlz.puma.gui.polarisation.PolarisationPanel'),
            setups='polarization* or defcal',
        ),
]

tools = [
    tool('Downtime report', 'nicos.clients.gui.tools.downtime.DownTimeTool',
         sender='puma@frm2.tum.de',
    ),
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
]
