description = 'cascade psd detector'

includes = ['detector']

devices = dict(
    dtx    = device('devices.taco.Axis',
                    tacodevice = 'mira/axis/dtx',
                    abslimits = (0, 1500),
                    pollinterval = 5,
                    maxage = 10),
)
