description = 'LakeShore 340 cryo controller for CCR-5 cryostat'
group = 'optional'

includes = ['alias_T']

modules = ['nicos.mira.commands']

devices = dict(
    T_ccr5   = device('devices.taco.TemperatureController',
                      tacodevice = '//mirasrv/mira/ls340/control',
                      pollinterval = 0.7,
                      maxage = 2,
                      abslimits = (0, 300)),
    T_ccr5_A = device('devices.taco.TemperatureSensor',
                      tacodevice = '//mirasrv/mira/ls340/a',
                      pollinterval = 0.7,
                      maxage = 2),
    T_ccr5_B = device('devices.taco.TemperatureSensor',
                      tacodevice = '//mirasrv/mira/ls340/b',
                      pollinterval = 0.7,
                      maxage = 2),
    T_ccr5_C = device('devices.taco.TemperatureSensor',
                      tacodevice = '//mirasrv/mira/ls340/c',
                      pollinterval = 0.7,
                      maxage = 2),
    ccr5_p1  = device('devices.taco.AnalogInput',
                      description = 'Cryo sample tube pressure',
                      tacodevice = '//mirasrv/mira/ccr/p1',
                      fmtstr = '%.3f'),
    ccr5_p2  = device('devices.taco.AnalogInput',
                      description = 'Cryo sample tube pressure (second sensor)',
                      tacodevice = '//mirasrv/mira/ccr/p2',
                      fmtstr = '%.3f'),
    ccr5_compressor_switch = device('devices.taco.NamedDigitalOutput',
                                    mapping = {'off': 0, 'on': 1},
                                    tacodevice = '//mirasrv/mira/ccr/pump',),
    ccr5_gas_switch        = device('mira.ccr.GasValve',
                                    mapping = {'off': 0, 'on': 1},
                                    tacodevice = '//mirasrv/mira/ccr/gas',
                                    timeout = 600),
    ccr5_vacuum_switch     = device('devices.taco.NamedDigitalOutput',
                                    mapping = {'off': 0, 'on': 1},
                                    tacodevice = '//mirasrv/mira/ccr/vacuum'),
)

startupcode = '''
T.alias = T_ccr5
Ts.alias = T_ccr5_A
'''
