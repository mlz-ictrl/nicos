description = 'Instrument shutter device'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    shutter_m = device('nicos.devices.taco.Motor',
                       description = 'Instrument shutter linear motor',
                       tacodevice = '%s/shutter/motor' % tacodev,
                       abslimits = (0, 55),
                       precision = 0.5,
                       lowlevel = True,
                      ),
    shutter = device('nicos.devices.generic.Switcher',
                     description = 'Instrument shutter',
                     moveable = 'shutter_m',
                     precision = 0.5,
                     mapping = {'closed': 0, 'open': 55},
                     fallback = 'offline',
                    ),
)
