description = 'plug-and-play magnet sample environment'
group = 'optional'

includes = ['alias_B']

devices = dict(
    B_virt = device('nicos.devices.generic.VirtualMotor',
        description = 'virtual "magnetic field"',
        abslimits = (-10, 10),
        unit = 'T'
    ),
    magnet_current = device('nicos.devices.generic.VirtualMotor',
        description = 'current source for magnet test',
        abslimits = (-250, 250),
        unit = 'A',
        ramp = 1.,
    ),
    B_magnet = device('nicos.devices.generic.CalibratedMagnet',
        description = 'magnetic field device, handling '
        'polarity switching and stuff',
        currentsource = 'magnet_current',
        unit = 'T',
        calibration = (0.000872603, -0.0242964, 0.0148907, 0.0437158,
                       0.0157436),
        abslimits = (-0.5, 0.5),
    ),
)

alias_config = {
    'B': {'B_magnet': 100, 'B_virt': 0},
}
