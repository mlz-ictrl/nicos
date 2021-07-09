description = 'Slit H2 using Beckhoff controllers'

group = 'lowlevel'

devices = dict(
    h2l = device('nicos.devices.generic.VirtualMotor',
        description = 'left slit motor',
        abslimits = (-69.5, 0),
        unit = 'mm',
        lowlevel = True,
    ),
    h2r = device('nicos.devices.generic.VirtualMotor',
        description = 'right slit motor',
        abslimits = (0, 69.5),
        unit = 'mm',
        lowlevel = True,
    ),
    h2 = device('nicos_mlz.refsans.devices.slits.Gap',
        description = 'Horizontal slit system',
        left = 'h2l',
        right = 'h2r',
        opmode = 'offcentered',
    ),
    h2_center = device('nicos.devices.generic.DeviceAlias'),
    h2_width = device('nicos.devices.generic.DeviceAlias'),
)

alias_config = {
    'h2_width':  {'h2.width': 100},
    'h2_center': {'h2.center': 100},
}
