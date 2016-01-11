description = 'Single Slit'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    bs1_m = device('devices.taco.Motor',
                   description = 'SlitMotor reactor side',
                   tacodevice = '%s/bs1/mr' % tacodev,
                   abslimits = (-215.69,93.0),
                  ),
)
