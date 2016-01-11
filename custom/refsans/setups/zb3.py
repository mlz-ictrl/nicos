description = "Double Slit"

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    zb3_mr = device('devices.taco.Motor',
                    description = 'SlitMotor reactor side',
                    tacodevice = '%s/zb3/mr' % tacodev,
                    abslimits = (-221, 95),
                   ),
    zb3_ms = device('devices.taco.Motor',
                    description = 'SlitMotor sample side',
                    tacodevice = '%s/zb3/ms' % tacodev,
                    abslimits = (-106, 113.562),
                   ),
)
