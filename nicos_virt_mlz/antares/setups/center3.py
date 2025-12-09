description = 'Helium pressures'

group = 'lowlevel'

devices = dict(
    center3_sens1 = device('nicos.devices.generic.ManualMove',
        description = 'Center 3 Sensor 1',
        default = 3.5e-6,
        abslimits = (0, 1000),
        fmtstr = '%.1g',
        unit = 'mbar',
    ),
    center3_sens2 = device('nicos.devices.generic.ManualMove',
        description = 'Center 3 Sensor 2',
        default = 3.5e-6,
        abslimits = (0, 1000),
        fmtstr = '%.1g',
        unit = 'mbar',
    ),
    He_pressure = device('nicos.devices.generic.ManualMove',
        description = 'Pressure of He bottle',
        default = 69.4,
        abslimits = (0, 100),
        fmtstr = '%.1g',
        unit = 'bar',
    ),
)
