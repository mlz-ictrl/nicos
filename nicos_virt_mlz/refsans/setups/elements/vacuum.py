description = 'Vacuum readout devices using Leybold Center 3'

group = 'lowlevel'

devices = dict(
    vacuum_CB = device('nicos.devices.generic.ManualMove',
        description = 'Pressure in Chopper chamber',
        default = 3.5e-6,
        abslimits = (0, 1000),
        unit = 'mbar',
        fmtstr = '%.1g',
    ),
    vacuum_SFK = device('nicos.devices.generic.ManualMove',
        description = 'Pressure in beam guide chamber',
        default = 1.9e-6,
        abslimits = (0, 1000),
        unit = 'mbar',
        fmtstr = '%.1g',
    ),
    vacuum_SR = device('nicos.devices.generic.ManualMove',
        description = 'Pressure in scattering tube',
        default = 2.7e-6,
        abslimits = (0, 1000),
        unit = 'mbar',
        fmtstr = '%.1g',
    ),
)
