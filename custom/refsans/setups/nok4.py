description = 'nok4'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    nok4_mr = device('devices.taco.Motor',
                     description = 'nokMotor reactor side',
                     tacodevice = '%s/nok4/mr' % tacodev,
                     abslimits = (-20.477, 48.523),
                    ),
    nok4_ms = device('devices.taco.Motor',
                     description = 'nokMotor sample side',
                     tacodevice = '%s/nok4/ms' % tacodev,
                     abslimits = (-21.302, 41.197),
                    ),
)
