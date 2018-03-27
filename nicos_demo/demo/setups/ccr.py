description = 'for testing the frm2.ccr module'

group = 'optional'

includes = ['cryo']

devices = dict(
    T_stick = device('nicos.devices.generic.VirtualTemperature',
        description = 'Temperature control of the stick',
        abslimits = (2, 600),
        warnlimits = (0, 600),
        speed = 6,
        unit = 'K',
    ),
    T_tube = device('nicos.devices.generic.VirtualTemperature',
        description = 'Temperature control of the cryo tube',
        abslimits = (0, 300),
        warnlimits = (0, 300),
        speed = 6,
        unit = 'K',
    ),
    T_ccr = device('nicos_mlz.devices.ccr.CCRControl',
        description = 'Control device to regulate sample temperature via tube '
                      'and stick heater',
        stick = 'T_stick',
        tube = 'T_tube',
    ),
)

alias_config = {
    'T': {'T_ccr': 150},
    'Ts': {'T_stick': 150, 'T_tube': 80},
}
