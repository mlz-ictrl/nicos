description = 'LakeShore 340 cryo controller for CC PUMA cryostat'
group = 'optional'

includes = ['alias_T']

devices = dict(
    T_cc   = device('devices.taco.TemperatureController',
                      description = 'CC PUMA temperature regulation',
                      tacodevice = '//antaressrv/antares/ls340/control',
                      pollinterval = 1,
                      maxage = 6,
                      abslimits = (0, 300),
                     ),
    T_cc_A = device('devices.taco.TemperatureSensor',
                      description = 'CC sensor A',
                      tacodevice = '//antaressrv/antares/ls340/sensa',
                      pollinterval = 1,
                      maxage = 6,
                     ),
    T_cc_B = device('devices.taco.TemperatureSensor',
                      description = 'CC sensor B',
                      tacodevice = '//antaressrv/antares/ls340/sensb',
                      pollinterval = 1,
                      maxage = 6,
                     ),
)
alias_config = [
    ('T', 'T_cc', 100),
    ('Ts', 'T_cc_B', 100),
    ('Ts', 'T_cc_A', 90),
]
