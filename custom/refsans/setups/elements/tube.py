description = "raise of detector"

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    tube_m = device('nicos.devices.taco.Motor',
                    description = 'tube Motor',
                    tacodevice = '%s/servostar/tube0' % tacodev,
                    abslimits = (-120, 1000),
                    lowlevel = True,
                   ),
    tube = device('nicos.devices.generic.Axis',
                   description = 'tube height',
                   motor = 'tube_m',
                   obs = [],
                   precision = 0.05,
                   dragerror = 10.,
                  ),
)
