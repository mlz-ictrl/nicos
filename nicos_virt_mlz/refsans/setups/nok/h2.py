description = 'Slit H2 using Beckhoff controllers'

group = 'lowlevel'

devices = dict(
    h2l = device('nicos.devices.generic.VirtualMotor',
        description = 'left slit motor',
        abslimits = (-77, 58.3),
        unit = 'mm',
        visibility = (),
    ),
    h2r = device('nicos.devices.generic.VirtualMotor',
        description = 'right slit motor',
        abslimits = (-58.3, 77),
        unit = 'mm',
        visibility = (),
    ),
    h2 = device('nicos.devices.generic.slit.HorizontalGap',
        description = 'Horizontal slit system',
        left = 'h2l',
        right = 'h2r',
        opmode = 'offcentered',
        min_opening = -1,
    ),
    h2_center = device('nicos.devices.generic.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.CenterGapAxis',
        alias = 'h2.center',
    ),
    h2_width = device('nicos.devices.generic.DeviceAlias',
        devclass = 'nicos.devices.generic.slit.SizeGapAxis',
        alias = 'h2.width',
    ),
)

alias_config = {
    'h2_width':  {'h2.width': 100},
    'h2_center': {'h2.center': 100},
}
