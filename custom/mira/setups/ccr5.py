description = 'LakeShore 340 cryo controller for CCR-5 cryostat'
group = 'optional'

includes = ['alias_T']

modules = ['nicos.mira.commands']

devices = dict(
    T_ccr5   = device('devices.taco.TemperatureController',
                      description = 'CCR5 temperature regulation',
                      tacodevice = '//mirasrv/mira/ls340/control',
                      pollinterval = 0.7,
                      maxage = 2,
                      abslimits = (0, 300),
                     ),
    T_ccr5_A = device('devices.taco.TemperatureSensor',
                      description = 'CCR5 sensor A',
                      tacodevice = '//mirasrv/mira/ls340/a',
                      pollinterval = 0.7,
                      maxage = 2,
                     ),
    T_ccr5_B = device('devices.taco.TemperatureSensor',
                      description = 'CCR5 sensor B',
                      tacodevice = '//mirasrv/mira/ls340/b',
                      pollinterval = 0.7,
                      maxage = 2,
                     ),
    T_ccr5_C = device('devices.taco.TemperatureSensor',
                      description = 'CCR5 sensor C',
                      tacodevice = '//mirasrv/mira/ls340/c',
                      pollinterval = 0.7,
                      maxage = 2,
                     ),
    ccr5_p1  = device('devices.taco.AnalogInput',
                      description = 'Cryo sample tube pressure',
                      tacodevice = '//mirasrv/mira/ccr/p1',
                      fmtstr = '%.3f',
                     ),
#    ccr5_p2  = device('devices.taco.AnalogInput',
#                      description = 'Cryo sample tube pressure (second sensor)',
#                      tacodevice = '//mirasrv/mira/ccr/p2',
#                      fmtstr = '%.3f',
#                     ),
    ccr5_compressor_switch = device('devices.taco.NamedDigitalOutput',
                                    description = 'CCR5 compressor switch on/off',
                                    mapping = {'off': 0, 'on': 1},
                                    tacodevice = '//mirasrv/mira/ccr/pump',
                                   ),
    ccr5_gas_switch        = device('devices.taco.NamedDigitalOutput',
                                    description = 'CCR5 sample tube gas switch on/off',
                                    mapping = {'off': 0, 'on': 1},
                                    tacodevice = '//mirasrv/mira/ccr/gas',
                                   ),
    ccr5_vacuum_switch     = device('devices.taco.NamedDigitalOutput',
                                    description = 'CCR5 sample tube vacuum switch on/off',
                                    mapping = {'off': 0, 'on': 1},
                                    tacodevice = '//mirasrv/mira/ccr/vacuum',
                                   ),
)

startupcode = '''
T.alias = T_ccr5
Ts.alias = T_ccr5_A
'''
