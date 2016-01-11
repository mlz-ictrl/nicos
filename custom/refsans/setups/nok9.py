description = 'nok9'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    nok9_mr = device('devices.taco.Motor',
                     description = 'nokMotor reactor side',
                     tacodevice = '%s/nok9/mr' % tacodev,
                     abslimits = (-112.03425, 142.95925),
                    ),
    nok9_ms = device('devices.taco.Motor',
                     description = 'nokMotor sample side',
                     tacodevice = '%s/nok9/ms' % tacodev,
                     abslimits = (-114.51425, 142.62775),
                    ),
)
