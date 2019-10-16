description = 'Sample slit devices'

group = 'lowlevel'

excludes = ['slits']
includes = ['motorbox01']

devices = dict(
    slits = device('nicos.devices.generic.Slit',
        description = 'sample slit 4 blades',
        left = 'slits_l',
        right = 'slits_r',
        bottom = 'slits_d',
        top = 'slits_u',
        opmode = 'centered',
        coordinates = 'opposite',
        pollinterval = 60,
        maxage = 90,
    ),
)
