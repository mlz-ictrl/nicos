description = 'Slit H2 using Beckhoff controllers'

group = 'lowlevel'

devices = dict(
    h2 = device('nicos.devices.generic.slit.HorizontalGap',
        description = 'Horizontal slit system',
        left = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-30, 30),
            unit = 'mm',
        ),
        right = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-30, 30),
            unit = 'mm',
        ),
        opmode = 'offcentered',
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
