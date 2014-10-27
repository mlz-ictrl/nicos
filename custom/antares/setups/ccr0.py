description = 'LakeShore 360 cryo controller for CCR-0 cryostat'
group = 'optional'

includes = ['alias_T']

devices = dict(
    T_ccr0   = device('devices.taco.TemperatureController',
                      description = 'CCR0 temperature regulation',
                      tacodevice = '//antaressrv/antares/ls340/control',
                      pollinterval = 1,
                      maxage = 6,
                      abslimits = (0, 300)),
    T_ccr0_A = device('devices.taco.TemperatureSensor',
                      description = 'CCR0 sensor A',
                      tacodevice = '//antaressrv/antares/ls340/sensa',
                      pollinterval = 1,
                      maxage = 6),
    T_ccr0_B = device('devices.taco.TemperatureSensor',
                      description = 'CCR0 sensor B',
                      tacodevice = '//antaressrv/antares/ls340/sensb',
                      pollinterval = 1,
                      maxage = 6),
    T_ccr0_C = device('devices.taco.TemperatureSensor',
                      description = 'CCR0 sensor C',
                      tacodevice = '//antaressrv/antares/ls340/sensc',
                      pollinterval = 1,
                      maxage = 6),
    T_ccr0_D = device('devices.taco.TemperatureSensor',
                      description = 'CCR0 sensor D',
                      tacodevice = '//antaressrv/antares/ls340/sensd',
                      pollinterval = 1,
                      maxage = 6),
    ccr0_p1  = device('devices.taco.AnalogInput',
                      description = 'Cryo sample tube pressure',
                      tacodevice = '//antaressrv/antares/ccr/p1',
                      fmtstr = '%.3f'),
    ccr0_p2  = device('devices.taco.AnalogInput',
                      description = 'Cryo sample tube pressure (second sensor)',
                      tacodevice = '//antaressrv/antares/ccr/p2',
                      fmtstr = '%.3f'),
    ccr0_compressor_switch = device('devices.taco.NamedDigitalOutput',
                                    description = 'CCR0 compressor switch on/off',
                                    mapping = {'off': 0, 'on': 1},
                                    tacodevice = '//antaressrv/antares/ccr/pump',),
    ccr0_gas_switch        = device('devices.taco.NamedDigitalOutput',
                                    description = 'CCR0 sample tube gas switch on/off',
                                    mapping = {'off': 0, 'on': 1},
                                    tacodevice = '//antaressrv/antares/ccr/gas'),
    ccr0_vacuum_switch     = device('devices.taco.NamedDigitalOutput',
                                    description = 'CCR0 sample tube vacuum switch on/off',
                                    mapping = {'off': 0, 'on': 1},
                                    tacodevice = '//antaressrv/antares/ccr/vacuum'),
)

startupcode = '''
T.alias = T_ccr0
Ts.alias = T_ccr0_A
'''
