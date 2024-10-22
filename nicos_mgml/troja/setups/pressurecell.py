description = 'Pressure cell'

group = 'optional'

devices = dict(
    pressure = device('nicos.devices.generic.ManualMove',
        description = 'pressure in the pressure cell (at room temperature)',
        default = 0,
        unit = 'kbar',
        fmtstr = '%.3f',
        abslimits = (0, 500),
    ),
)
