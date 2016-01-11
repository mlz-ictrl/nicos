description = "sc2 height"

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    sc2 = device('devices.taco.Motor',
                 description = 'sc2 Motor',
                 tacodevice = '%s/sc2/motor' % tacodev,
                 abslimits = (-150, 150),
                ),
)
