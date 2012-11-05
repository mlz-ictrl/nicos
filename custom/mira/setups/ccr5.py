description = 'LakeShore 340 cryo controller for CCR-5 cryostat'
group = 'optional'

includes = ['alias_T']

modules = ['nicos.mira.commands']

devices = dict(
    T_ccr5   = device('devices.taco.TemperatureController',
                      tacodevice = 'mira/ls340/control',
                      pollinterval = 0.7,
                      maxage = 2,
                      abslimits = (0, 300)),
    T_ccr5_A = device('devices.taco.TemperatureSensor',
                      tacodevice = 'mira/ls340/a',
                      pollinterval = 0.7,
                      maxage = 2),
    T_ccr5_B = device('devices.taco.TemperatureSensor',
                      tacodevice = 'mira/ls340/b',
                      pollinterval = 0.7,
                      maxage = 2),
    T_ccr5_C = device('devices.taco.TemperatureSensor',
                      tacodevice = 'mira/ls340/c',
                      pollinterval = 0.7,
                      maxage = 2),
    ccr5_p1  = device('devices.taco.AnalogInput',
                      description = 'Cryo sample tube pressure',
                      tacodevice = 'mira/ccr/p1',
                      fmtstr = '%.3f'),
    ccr5_compressor_switch = device('devices.taco.NamedDigitalOutput',
                      mapping = {0: 'off', 1: 'on'},
                      tacodevice = 'mira/ccr/pump',),
    ccr5_gas_switch = device('mira.ccr.GasValve',
                      mapping = {0: 'off', 1: 'on'},
                      tacodevice = 'mira/ccr/gas',
                      timeout = 600),
    ccr5_vacuum_switch = device('devices.taco.NamedDigitalOutput',
                      mapping = {0: 'off', 1: 'on'},
                      tacodevice = 'mira/ccr/vacuum'),
)

startupcode = '''
T.alias = T_ccr5
Ts.alias = T_ccr5_A
'''
