description = 'double slit'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    bs1_mr = device('devices.taco.Motor',
                    description = 'SlitMotor reactor side',
                    tacodevice = '%s/bs1/mr' % tacodev,
                    abslimits = (-178.0, -0.7),
                   ),
    bs1_ms = device('devices.taco.Motor',
                    description = 'SlitMotor sample side',
                    tacodevice = '%s/bs1/ms' % tacodev,
                    abslimits = (-177.002, 139.998),
                   ),
)
