description = "disc4 height"

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    disc4 = device('nicos.devices.taco.Motor',
                   description = 'disc 4 Motor',
                   tacodevice = '%s/disk4/motor' % tacodev,
                   abslimits = (-22, 49.5),
                  ),
)
