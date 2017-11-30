description = 'backguard: after sample'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost


devices = dict(
    backguard = device('nicos.devices.taco.Motor',
        description = 'Backgard axis motor',
        tacodevice = '%s/phytron/kanal_07' % tacodev,
        abslimits = (-0.5, 31.0),
    ),
)
