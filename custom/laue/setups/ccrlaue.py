description = 'LakeShore 340 cryo controller for CCR-laue cryostat'
group = 'optional'

includes = ['alias_T']

devices = dict(
    T_laue   = device('devices.taco.TemperatureController',
                      description = 'CCR laue temperature regulation',
                      tacodevice = '//lauectrl.laue.frm2/laue/ls340/control',
                      pollinterval = 0.7,
                      maxage = 2,
                      abslimits = (0, 325),
                     ),
    T_laue_A = device('devices.taco.TemperatureSensor',
                      description = 'laue sensor A',
                      tacodevice = '//lauectrl.laue.frm2/laue/ls340/sensa',
                      pollinterval = 0.7,
                      maxage = 2,
                     ),
    T_laue_B = device('devices.taco.TemperatureSensor',
                      description = 'laue sensor B',
                      tacodevice = '//lauectrl.laue.frm2/laue/ls340/sensb',
                      pollinterval = 0.7,
                      maxage = 2,
                     ),
    ccrlaue_compressor_switch = device('devices.taco.NamedDigitalOutput',
                                    description = 'laue compressor switch on/off',
                                    mapping = {'off': 0, 'on': 1},
                                    tacodevice = '//lauectrl.laue.frm2/laue/ls340/relais1',
                                   ),

)

alias_config = {
    'T':  {'T_laue': 100},
    'Ts': {'T_laue_B': 100, 'T_laue_A': 90},
}
