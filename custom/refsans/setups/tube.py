description = "raise of detector"

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    tube_m = device('devices.taco.Motor',
                    description = 'tube Motor',
                    tacodevice = '%s/servostar/tube0' % tacodev,
                    abslimits = (-120, 1000),
                   ),
)
