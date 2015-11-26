
description = 'Sample table devices'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost


devices = dict(
    theta_m = device('devices.taco.Motor',
                     description = 'Theta axis motor',
                     tacodevice = '%s/phytron/kanal_01' % tacodev,
                     abslimits = (-15, 15),
                     lowlevel = True,
                    ),
    theta = device('devices.generic.Axis',
                   description = 'Theta axis',
                   motor = 'theta_m',
                   coder = 'theta_m',
                   precision = 0.01,
                  ),
)

startupcode = '''
'''
