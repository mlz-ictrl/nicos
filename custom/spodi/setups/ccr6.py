description = 'LakeShore 340 cryo controller for CCR-6 cryostat'
group = 'optional'

includes = ['alias_T']

nethost = 'spodisrv'
domain = 'spodi'

devices = dict(
    T_ccr6 = device('devices.taco.TemperatureController',
        description = 'CCR6 temperature regulation',
        tacodevice = '//%s/%s/ls340/control' % (nethost, domain),
        pollinterval = 1,
        maxage = 6,
        abslimits = (0, 300),
    ),
    T_ccr6_A = device('devices.taco.TemperatureSensor',
        description = 'CCR6 sensor A',
        tacodevice = '//%s/%s/ls340/sensora' % (nethost, domain),
        pollinterval = 1,
        maxage = 6,
    ),
    T_ccr6_B = device('devices.taco.TemperatureSensor',
        description = 'CCR6 sensor B',
        tacodevice = '//%s/%s/ls340/sensorb' % (nethost, domain),
        pollinterval = 1,
        maxage = 6,
    ),
    # T_ccr6_C = device('devices.taco.TemperatureSensor',
    #     description = 'CCR6 sensor C',
    #     tacodevice = '//%s/%s/ls340/sensc' % (nethost, domain),
    #     pollinterval = 1,
    #     maxage = 6,
    # ),
    # T_ccr6_D = device('devices.taco.TemperatureSensor',
    #     description = 'CCR6 sensor D',
    #     tacodevice = '//%s/%s/ls340/sensd' % (nethost, domain),
    #     pollinterval = 1,
    #     maxage = 6,
    # ),
    # ccr6_p1 = device('devices.taco.AnalogInput',
    #     description = 'Cryo sample tube pressure',
    #     tacodevice = '//%s/%s/ccr/p1' % (nethost, domain),
    #     fmtstr = '%.3f',
    # ),
    # ccr6_p2 = device('devices.taco.AnalogInput',
    #     description = 'Cryo sample tube pressure (second sensor)',
    #     tacodevice = '//%s/%s/ccr/p2' % (nethost, domain),
    #     fmtstr = '%.3f',
    # ),
    # ccr6_compressor_switch = device('devices.taco.NamedDigitalOutput',
    #     description = 'CCR6 compressor switch on/off',
    #     mapping = {'off': 0,
    #                'on': 1},
    #     tacodevice = '//%s/%s/ccr/pump' % (nethost, domain),
    # ),
    # ccr6_gas_switch = device('devices.taco.NamedDigitalOutput',
    #     description = 'CCR6 sample tube gas switch on/off',
    #     mapping = {'off': 0,
    #                'on': 1},
    #     tacodevice = '//%s/%s/ccr/gas' % (nethost, domain),
    # ),
    # ccr6_vacuum_switch = device('devices.taco.NamedDigitalOutput',
    #     description = 'CCR6 sample tube vacuum switch on/off',
    #     mapping = {'off': 0,
    #                'on': 1},
    #     tacodevice = '//%s/%s/ccr/vacuum' % (nethost, domain),
    # ),
)

alias_config = {
    'T': {
        'T_ccr6': 100
    },
    'Ts': {
        'T_ccr6_A': 100,
        'T_ccr6_B': 90,
        # 'T_ccr6_C': 80,
        # 'T_ccr6_D': 70
    },
}
