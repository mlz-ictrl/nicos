description = 'Y-Z table combination'
group = 'plugplay'

devices = dict(
    dty = device('nicos.devices.taco.Motor',
                 description = 'horizontal table',
                 tacodevice = '//phytronpi01/raspi/motor/x1',
                 abslimits = (-100, 100),
                 unit = 'mm',
                ),
    dtz = device('nicos.devices.taco.Motor',
                 description = 'vertical table',
                 tacodevice = '//phytronpi01/raspi/motor/x2',
                 abslimits = (-100, 100),
                 unit = 'mm',
                ),
)
