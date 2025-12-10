"""NICOS GUI default configuration."""

main_window = docked(
    tabbed(
#       ('Funktionen',
#        docked(
#           panel('nicos_mlz.firepod.gui.panels.dynamicpanel.FirepodDynamicPanel'),
#        ),
#       ),
        ('Command line',
         vsplit(
            panel('nicos.clients.gui.panels.cmdbuilder.CommandPanel',
                  modules=['nicos_mlz.firepod.gui.cmdlets'],
                  scanlist=['hv1'],
                  movelist=['omgs', 'tths', 'xs', 'ys', 'bs', 'collimator', 'filter', 'laser', 'shutter', 'rc', ],
            ),
            panel('nicos.clients.gui.panels.status.ScriptStatusPanel', eta=True),
            panel('nicos.clients.gui.panels.console.ConsolePanel',
                  watermark='nicos_demo/demo/gui/nicos-watermark.png', hasinput=False),
         ),
        ),
        ('NICOS devices',
         panel('nicos.clients.gui.panels.devices.DevicesPanel',
           param_display={
               'Exp': [
                   'lastpoint',
                   'lastscan',
                ],
               'slit': ['opmode',],
           },
           filters=[
               ('Detector', 'det'),
               ('Temperatures', '^T'),
               ('Sample table', '(omgs|tths|xs|ys)'),
           ],
          ),
        ),
    ),
)
