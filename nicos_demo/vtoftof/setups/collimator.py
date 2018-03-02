description = 'neutron guide changer or collimator'

group = 'lowlevel'

devices = dict(
    ngc = device('nicos_mlz.toftof.devices.neutronguide.Switcher',
        description = 'The neutron guide changer/collimator',
        moveable = device('nicos.devices.generic.VirtualMotor',
            fmtstr = "%7.2f",
            abslimits = (-131.4, 0.),
            unit = 'mm',
            lowlevel = True,
            speed = 2,
            curvalue = -5.1,
        ),
        mapping = {
            'linear': -5.1,
            'focus': -131.25,
        },
    ),
)
