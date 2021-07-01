description = 'Pressure sensors'

group = 'optional'

devices = dict(
    P_ng_elements = device('nicos.devices.generic.ManualMove',
        description = 'Pressure in the neutron guide elements',
        abslimits = (0, 1030),
        fmtstr = '%.1f',
        unit = 'mbar',
    ),
    P_polarizer = device('nicos.devices.generic.ManualMove',
        description = 'Polarizer pressure',
        abslimits = (0, 1030),
        fmtstr = '%.1f',
        unit = 'mbar',
    ),
    P_selector_vacuum = device('nicos.devices.generic.ManualMove',
        description = 'Selector vacuum pressure',
        abslimits = (0, 1030),
        fmtstr = '%.4f',
        unit = 'mbar',
    ),
)
