description = 'Various devices for HRPT'

devices = dict(
    d1l = device('nicos.devices.generic.VirtualMotor',
        description = 'Slit left blade',
        unit = 'egu',
        abslimits = (0, 100),
    ),
    d1r = device('nicos.devices.generic.VirtualMotor',
        description = 'Slit right blade',
        unit = 'egu',
        abslimits = (0, 100),
    ),
    slit1 = device('nicos_sinq.hrpt.devices.slit.Gap',
        left = 'd1l',
        right = 'd1r',
        unit = 'mm',
        opmode = 'centered',
        coordinates = 'opposite',
        conversion_factor = 22.66
    ),
)
