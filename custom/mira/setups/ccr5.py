description = 'LakeShore 340 cryo controller for CCR-5 cryostat'
group = 'optional'

includes = ['alias_T']

modules = ['nicos.mira.commands']

tango_url = 'tango://mira1.mira.frm2:10000/mira/'

devices = dict(
    T_ccr5   = device('devices.taco.TemperatureController',
                      description = 'CCR5 temperature regulation',
                      tacodevice = '//mirasrv/mira/ls340/control',
                      pollinterval = 0.7,
                      maxage = 2,
                      abslimits = (0, 325),
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
    ccr5_p1  = device('devices.tango.AnalogInput',
                      description = 'cryo sample tube pressure',
                      tangodevice = tango_url + 'ccr5/p1',
                      fmtstr = '%.3f',
                     ),
#    ccr5_p2  = device('devices.tango.AnalogInput',
#                      description = 'Cryo sample tube pressure (second sensor)',
#                      tangodevice = tango_url + 'ccr5/p2',
#                      fmtstr = '%.3f',
#                     ),
    ccr5_compressor_switch = device('devices.tango.NamedDigitalOutput',
                                    description = 'CCR5 compressor switch on/off',
                                    mapping = {'off': 0, 'on': 1},
                                    tangodevice = tango_url + 'ccr5/comp',
                                   ),
    ccr5_gas_switch        = device('devices.tango.NamedDigitalOutput',
                                    description = 'CCR5 sample tube gas switch on/off',
                                    mapping = {'off': 0, 'on': 1},
                                    tangodevice = tango_url + 'ccr5/gas',
                                   ),
    ccr5_vacuum_switch     = device('devices.tango.NamedDigitalOutput',
                                    description = 'CCR5 sample tube vacuum switch on/off',
                                    mapping = {'off': 0, 'on': 1},
                                    tangodevice = tango_url + 'ccr5/vacuum',
                                   ),
)

alias_config = {
    'T': {'T_ccr5': 200},
    'Ts': {'T_ccr5_A': 100, 'T_ccr5_B': 90, 'T_ccr5_C': 70},
}
