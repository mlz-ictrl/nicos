description = 'LakeShore 340 cryo controller for CCR-4 cryostat'
group = 'optional'

includes = ['alias_T']

devices = dict(
    T_ccr4   = device('devices.taco.TemperatureController',
                       description = 'Temperature Controller',
                       tacodevice = 'antares/ls340/control',
                       pollinterval = 3.,
                       maxage = 12.5,
                       abslimits = (0, 300),
                     ),
    T_ccr4_A = device('devices.taco.TemperatureSensor',
                       description = 'Temperature Sensor A',
                       tacodevice = 'antares/ls340/sensa',
                       pollinterval = 5.,
                       maxage = 12.5,
                     ),
    T_ccr4_B = device('devices.taco.TemperatureSensor',
                       description = 'Temperature Sensor B',
                       tacodevice = 'antares/ls340/sensb',
                       pollinterval = 5.,
                       maxage = 12.5,
                     ),
    T_ccr4_C = device('devices.taco.TemperatureSensor',
                       description = 'Temperature Sensor A',
                       tacodevice = 'antares/ls340/sensc',
                       pollinterval = 5.,
                       maxage = 12.5,
                     ),
#    ccr4_p1  = device('devices.taco.AnalogInput',
#                      description = 'Cryo sample tube pressure',
#                      tacodevice = 'mira/ccr/p1',
#                      fmtstr = '%.3f'),
#    ccr4_compressor_switch = device('devices.taco.NamedDigitalOutput',
#                      mapping = {0: 'off', 1: 'on'},
#                      tacodevice = 'mira/ccr/pump',),
#    ccr4_gas_switch = device('mira.ccr.GasValve',
#                      mapping = {0: 'off', 1: 'on'},
#                      tacodevice = 'mira/ccr/gas',
#                      timeout = 600),
#    ccr4_vacuum_switch = device('devices.taco.NamedDigitalOutput',
#                      mapping = {0: 'off', 1: 'on'},
#                      tacodevice = 'mira/ccr/vacuum'),
)

startupcode = '''
T.alias = T_ccr4
Ts.alias = T_ccr4_A
'''
