description = 'support device(s) for pressure cells'

group = 'optional'

devices = dict(
    p_cell = device('devices.generic.ManualMove',
                    description = 'pressure in the pressure cell',
                    default = 0,
                    unit = 'kbar',
                    fmtstr = '%6.1f',
                    abslimits = (0, 500)
                   ),
)
