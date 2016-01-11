description = 'nok2'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    nok2_mr = device('devices.taco.Motor',
                     description = 'nokMotor reactor side',
                     tacodevice = '%s/nok2/mr' % tacodev,
                     abslimits = (-22.360, 10.880),
                    ),
    nok2_ms = device('devices.taco.Motor',
                     description = 'nokMotor sample side',
                     tacodevice = '%s/nok2/ms' % tacodev,
                     abslimits = (-21.610, 6.885),
                    ),
)
