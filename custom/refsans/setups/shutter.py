description = 'Instrument shutter device'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    shutter_m = device('devices.taco.Motor',
                       description = 'Instrument shutter linear motor',
                       tacodevice = '%s/shutter/motor' % tacodev,
                       abslimits = (0, 55),
                       lowlevel = True,
                      ),
    shutter = device('devices.generic.Switcher',
                     description = 'Instrument shutter',
                     moveable = 'shutter_m',
                     precision = .2,
                     mapping = {'close': 0, 'open': 55},
                    ),
)
