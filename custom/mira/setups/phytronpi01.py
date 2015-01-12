description = 'Y-Z table combination'

devices = dict(
    dty = device('devices.taco.Motor',
                 description = 'Horizontal table',
                 tacodevice = '//phytronpi01/raspi/motor/x1',
                 abslimits = (-100, 100),
                 unit = 'mm',
                ),
    dtz = device('devices.taco.Motor',
                 description = 'Vertical table',
                 tacodevice = '//phytronpi01/raspi/motor/x2',
                 abslimits = (-100, 100),
                 unit = 'mm',
                ),
)
