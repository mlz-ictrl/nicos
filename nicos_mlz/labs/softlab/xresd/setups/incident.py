# -*- coding: utf-8 -*-
description = 'incident optics'

group = 'optional'

devices = dict(
    i_col = device('nicos.devices.generic.ManualSwitch',
        description = 'Collimation diameter',
        unit = 'mm',
        states = ['None', 0.3, 0.5, 1.0, 1.5],
        # default = 0.3,
    ),
    i_filter = device('nicos.devices.generic.ManualSwitch',
        description = 'Kbeta filter',
        unit = '',
        states = ['None', 'V 10µm', 'Cu 100µm', 'Cu 200µm'],
    ),
)
