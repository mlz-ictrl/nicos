"""NICOS GUI default configuration."""

main_window = docked(
    tabbed(
        ('Commands', vsplit(

            panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),

            panel('nicos.clients.gui.panels.console.ConsolePanel'),

        )),
        ('Settings', panel('nicos_jcns.seop.gui.seop.SeopSettingsPanel')),
    ),
    ('NICOS devices', panel('nicos.clients.gui.panels.devices.DevicesPanel',
           param_display={'nmr_amplitude': 'sigma',
                          'nmr_t1': 'sigma',
                          'nmr_t2': 'sigma',
                          'nmr_frequency': 'sigma',
                          'nmr_phase': 'sigma',
                          'nmr_b': 'sigma',
                        }, icons=True, dockpos='right')
    ),
    ('Experiment Information and Setup',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',)
    ),
)

windows = [
    window('Editor', 'editor',
        vsplit(
            panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
            panel('nicos.clients.gui.panels.editor.EditorPanel',
              tools = [
                  tool('Scan Generator',
                       'nicos.clients.gui.tools.scan.ScanTool')
              ]))),
    window('Scans', 'plotter',
           panel('nicos.clients.gui.panels.scans.ScansPanel')),
    window('History', 'find',
           panel('nicos.clients.gui.panels.history.HistoryPanel')),
    window('Errors', 'errors',
           panel('nicos.clients.gui.panels.errors.ErrorPanel')),
    window('Watchdog', 'errors',
           panel('nicos.clients.gui.panels.watchdog.WatchdogPanel')),
    window('Spectrum', 'plotter',
            panel('nicos_jcns.seop.gui.seop.SeopPlotPanel',
            plotconf={'title':'Processed NMR Spectrum', 'xlabel':'Frequency', 'ylabel':'Intensity'},
            command = 'get_processed_spectrum',
                  )),
    window('Amplitude', 'plotter',
            panel('nicos_jcns.seop.gui.seop.SeopPlotPanel',
            plotconf={'title':'Amplitude Log', 'xlabel':'Time', 'ylabel':'Amplitude'},
            command = 'get_amplitude',
            xtime = True,
                  )),
    window('Signal', 'plotter',
            panel('nicos_jcns.seop.gui.seop.SeopPlotPanel',
            plotconf={'title':'Signal', 'xlabel':'Time', 'ylabel':'Amplitude'},
            command = 'get_processed_nmr',
                  )),
    window('Raw Spectrum', 'plotter',
            panel('nicos_jcns.seop.gui.seop.SeopPlotPanel',
            plotconf={'title':'Raw Spectrum', 'xlabel':'Time', 'ylabel':'Amplitude'},
            command = 'get_raw_spectrum',
                  )),
    window('Raw Signal', 'plotter',
            panel('nicos_jcns.seop.gui.seop.SeopPlotPanel',
            plotconf={'title':'Raw Signal', 'xlabel':'Raw Signal', 'ylabel':'Amplitude'},
            command = 'get_raw_nmr',
                  )),
    window('Phase', 'plotter',
            panel('nicos_jcns.seop.gui.seop.SeopPlotPanel',
            plotconf={'title':'Phase Log', 'xlabel':'Time', 'ylabel':'Phase'},
            command = 'get_phase',
            xtime = True,
                  )),
    window('Seop Quick Buttons', 'polarization',
           panel('nicos_jcns.seop.gui.seop.SeopControlPanel')),
]

tools = [
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    menu('Neutron helpers',
         tool('Neutron cross-sections',
              'nicos.clients.gui.tools.website.WebsiteTool',
              url='http://www.ncnr.nist.gov/resources/n-lengths/'),
         tool('Neutron activation',
              'nicos.clients.gui.tools.website.WebsiteTool',
              url='https://webapps.frm2.tum.de/intranet/activation/'),
         tool('Neutron calculations',
              'nicos.clients.gui.tools.website.WebsiteTool',
              url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    ),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Emergency stop button',
         'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=False),
    tool('Seop Quick Buttons',# 'polarization',
           'nicos_jcns.seop.gui.seop.SeopControlButtons'),
]
