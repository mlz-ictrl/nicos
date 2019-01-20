description = 'backguard: after sample DEVELOPING'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

excludes = ['backguard']

devices = dict(
    bg2_1 = device('nicos.devices.taco.Motor',
        description = 'Backguard axis motor Beam right KWS',
        tacodevice = '%s/phytron/kanal_04' % tacodev,
        abslimits = (-0.5, 61.0),
    ),
    bg2_2 = device('nicos.devices.taco.Motor',
        description = 'Backguard axis motor Beam left TOFTOF',
        tacodevice = '%s/phytron/kanal_03' % tacodev,
        abslimits = (-0.5, 61.0),
    ),
)
