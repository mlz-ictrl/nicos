description = "disc3 height"

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    disc3 = device('nicos.devices.taco.Motor',
        description = 'disc 3 Motor',
        tacodevice = '%s/disk3/motor' % tacodev,
        abslimits = (-43, 49),
    ),
)
