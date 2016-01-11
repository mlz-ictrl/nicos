description = 'lead block'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    nok1_m = device('devices.taco.Motor',
                    description = 'nokMotor',
                    tacodevice = '%s/nok1/mr' % tacodev,
                    abslimits = (-56.119, 1.381),
                   ),
)
