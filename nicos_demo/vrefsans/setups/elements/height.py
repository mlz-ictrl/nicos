description = 'Sample surface position measurement'

group = 'optional'

devices = dict(
    height = device('nicos_mlz.refsans.devices.tristate.TriState',
        description = 'Sample surface position.',
        unit = 'mm',
        port = 'height_port',
    ),
    height_port = device('nicos.devices.generic.ManualMove',
        description = 'Sample surface position',
        abslimits = (-30, 30),
        unit = 'mm',
        lowlevel = True,
    ),
)
