description = 'LakeShore 370 cryo controller'
group = 'optional'

includes = ['alias_T']

tango_base = 'tango://localhost:10000/20t/'

devices = dict(
    T_A = device('nicos.devices.entangle.Sensor',
        description = 'sensor A',
        tangodevice = tango_base + 'ls372/tempa',
        pollinterval = 0.7,
        maxage = 2,
    ),
    T_6 = device('nicos.devices.entangle.Sensor',
        description = 'sensor 6',
        tangodevice = tango_base + 'ls372/temp6',
        pollinterval = 0.7,
        maxage = 2,
    ),
)

