description = 'nok6'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    nok6_mr = device('devices.taco.Motor',
                     description = 'nokMotor reactor side',
                     tacodevice = '%s/nok6/mr' % tacodev,
                     abslimits = (-66.2, 96.59125),
                    ),
    nok6_ms = device('devices.taco.Motor',
                     description = 'nokMotor sample side',
                     tacodevice = '%s/nok6/ms' % tacodev,
                     abslimits = (-81.0, 110.875),
                    ),
)
