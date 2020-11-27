description = 'neutron guide changer or collimator'

group = 'lowlevel'

tango_base = 'tango://tofhw.toftof.frm2.tum.de:10000/toftof/hubermc/'

devices = dict(
    ngc_motor = device('nicos.devices.tango.Motor',
        description = 'The TACO motor for the neutron guide changing '
        'mechanism',
        tangodevice = tango_base + 'ccmot',
        fmtstr = '%7.3f',
        userlimits = (-131.4, 0.),
        abslimits = (-131.4, 0.),
        requires = {'level': 'admin'},
        unit = 'mm',
        lowlevel = True,
    ),
    ngc = device('nicos_mlz.toftof.devices.neutronguide.Switcher',
        description = 'The neutron guide changer/collimator',
        moveable = 'ngc_motor',
        mapping = {
            'linear': -5.1,
            'focus': -131.25,
        },
        requires = {'level': 'admin'},
    ),
)
