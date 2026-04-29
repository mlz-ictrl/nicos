description = 'incident optics'
group = 'optional'

devices = dict(
    i_col = device('nicos.devices.generic.ManualSwitch',
        description = 'Collimation diameter',
        unit = 'mm',
        states = ['None', 0.05, 0.1, 0.2, 0.4, 0.6, 1.0, 2.0],
        # default = 0.3,
    ),
    i_filter = device('nicos.devices.generic.ManualSwitch',
        description = 'Kbeta filter',
        unit = '',
        states = ['None', '15 µm Ni'],
    ),
)
