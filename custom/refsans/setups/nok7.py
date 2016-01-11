description = 'nok7'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    nok7_mr = device('devices.taco.Motor',
                     description = 'nokMotor reactor side',
                     tacodevice = '%s/nok7/mr' % tacodev,
                     abslimits = (-89.475, 116.1),
                    ),
    nok7_ms = device('devices.taco.Motor',
                     description = 'nokMotor sample side',
                     tacodevice = '%s/nok7/ms' % tacodev,
                     abslimits = (-96.94, 125.55),
                    ),
)
