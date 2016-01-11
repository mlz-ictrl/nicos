description = 'nok8'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    nok8_mr = device('devices.taco.Motor',
                     description = 'nokMotor reactor side',
                     tacodevice = '%s/nok8/mr' % tacodev,
                     abslimits = (-102.835, 128.41),
                    ),
    nok8_ms = device('devices.taco.Motor',
                     description = 'nokMotor sample side',
                     tacodevice = '%s/nok8/ms' % tacodev,
                     abslimits = (-104.6, 131.636),
                    ),
)
