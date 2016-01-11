description = 'nok3'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    nok3_mr = device('devices.taco.Motor',
                     description = 'nokMotor reactor side',
                     tacodevice = '%s/nok3/mr' % tacodev,
                     abslimits = (-21.967, 47.782),
                    ),
    nok3_ms = device('devices.taco.Motor',
                     description = 'nokMotor sample side',
                     tacodevice = '%s/nok3/ms' % tacodev,
                     abslimits = (-20.943, 40.8055),
                    ),
)
