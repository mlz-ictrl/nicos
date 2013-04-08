description = 'cascade psd detector'

includes = ['detector']

devices = dict(
    dtx    = device('mira.axis.PhytronAxis',
                    tacodevice = 'mira/axis/dtx',
                    abslimits = (0, 1500),
                    pollinterval = 5,
                    maxage = 10),
)
