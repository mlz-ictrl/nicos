description = 'neutron guide changer/collimator'

group = 'lowlevel'

devices = dict(
    ngc_motor = device('nicos.devices.generic.virtual.VirtualMotor',
        description = 'Motor changing guide position',
        fmtstr = "%7.2f",
        userlimits = (-131.4, 0.),
        abslimits = (-131.4, 0.),
        requires = {'level': 'admin'},
        curvalue = -5.1,
        unit = 'mm',
        speed = 5.,
        lowlevel = True,
    ),
    ngc = device('nicos.devices.generic.Switcher',
        description = 'The neutron guide changer/collimator',
        moveable = 'ngc_motor',
        mapping = {
            'guide1': -5.1,
            'guide2': -61.25,
            'blocked': -131.25,
        },
        requires = {'level': 'admin'},
        precision = 0.05,
    ),
)
