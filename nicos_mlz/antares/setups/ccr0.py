description = 'LakeShore 360 cryo controller for CCR-0 cryostat'
group = 'optional'

includes = ['alias_T']

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/'

devices = dict(
    T_ccr0 = device('nicos.devices.tango.TemperatureController',
        description = 'CCR0 temperature regulation',
        tangodevice = tango_base + 'ls340/control',
        pollinterval = 1,
        maxage = 6,
        abslimits = (0, 300),
    ),
    T_ccr0_A = device('nicos.devices.tango.Sensor',
        description = 'CCR0 sensor A',
        tangodevice = tango_base + 'ls340/sensa',
        pollinterval = 1,
        maxage = 6,
    ),
    T_ccr0_B = device('nicos.devices.tango.Sensor',
        description = 'CCR0 sensor B',
        tangodevice = tango_base + 'ls340/sensb',
        pollinterval = 1,
        maxage = 6,
    ),
    # T_ccr0_C = device('nicos.devices.tango.Sensor',
    #     description = 'CCR0 sensor C',
    #     tangodevice = tango_base + 'ls340/sensc',
    #     pollinterval = 1,
    #     maxage = 6,
    # ),
    # T_ccr0_D = device('nicos.devices.tango.Sensor',
    #     description = 'CCR0 sensor D',
    #     tangodevice = tango_base + 'ls340/sensd',
    #     pollinterval = 1,
    #     maxage = 6,
    # ),
    ccr0_p1 = device('nicos.devices.tango.Sensor',
        description = 'Cryo sample tube pressure',
        tangodevice = tango_base + 'ccr/p1',
        fmtstr = '%.3f',
    ),
    ccr0_p2 = device('nicos.devices.tango.Sensor',
        description = 'Cryo sample tube pressure (second sensor)',
        tangodevice = tango_base + 'ccr/p2',
        fmtstr = '%.3f',
    ),
    ccr0_compressor_switch = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'CCR0 compressor switch on/off',
        mapping = {'off': 0,
                   'on': 1},
        tangodevice = tango_base + 'ccr/pump',
    ),
    ccr0_gas_switch = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'CCR0 sample tube gas switch on/off',
        mapping = {'off': 0,
                   'on': 1},
        tangodevice = tango_base + 'ccr/gas',
    ),
    ccr0_vacuum_switch = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'CCR0 sample tube vacuum switch on/off',
        mapping = {'off': 0,
                   'on': 1},
        tangodevice = tango_base + 'ccr/vacuum',
    ),
)

alias_config = {
    'T': {
        'T_ccr0': 100
    },
    'Ts': {
        'T_ccr0_A': 100,
        'T_ccr0_B': 90,
        # 'T_ccr0_C': 80,
        # 'T_ccr0_D': 70
    },
}
