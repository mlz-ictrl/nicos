description = 'LakeShore 340 cryo controller for CC PUMA cryostat'
group = 'optional'

includes = ['alias_T']

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/ls340/'

devices = dict(
    T_cc = device('nicos.devices.tango.TemperatureController',
        description = 'CC PUMA temperature regulation',
        tangodevice = tango_base + 'control',
        unit = 'K',
        pollinterval = 1,
        maxage = 6,
    ),
    T_cc_A = device('nicos.devices.tango.Sensor',
        description = 'CC sensor A', 
        tangodevice = tango_base + 'sensa',
        unit = 'K', 
        pollinterval = 1, 
        maxage = 6,
    ),
    T_cc_B = device('nicos.devices.tango.Sensor',
        description = 'CC sensor B',
        tangodevice = tango_base + 'sensb',
        unit = 'K', 
        pollinterval = 1,
        maxage = 6,
   ),
)

alias_config = {
    'T': {'T_cc': 100 },
    'Ts': {'T_cc_B': 100,
           'T_cc_A': 90,
          },
}
