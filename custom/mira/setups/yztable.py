description = 'Y-Z table combination'

devices = dict(
    dty = device('devices.taco.Motor',
                 tacodevice='//mirasrv/mira/motor/x1',
                 abslimits=(-100, 100),
                 unit='mm',
                ),
    dtz = device('devices.taco.Motor',
                 tacodevice='//mirasrv/mira/motor/x2',
                 abslimits=(-100, 100),
                 unit='mm',
                ),
)
