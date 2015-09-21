description = 'High-Tc superconducting magnet'

group = 'plugplay'

includes = ['alias_B']

taco_host = setupname

devices = dict(
    # by convention this needs to be B_%(setupname)s
    I_ccmhts01  = device('devices.taco.CurrentSupply',
                         description = 'current device',
                         tacodevice = '//%s/magnet/kepco/current' % taco_host,
                         unit = 'A',
                         abslimits = (-210, 210),
                        ),
    B_ccmhts01  = device('devices.generic.magnet.CalibratedMagnet',
                         description = 'magnetic field device',
                         currentsource = 'I_ccmhts01',
                         unit = 'mT',
                         abslimits = (-2250, 2250),
                         # curve from Juergen Peters
                         calibration = [9.52412, 1.9862, 31.6875, 195.56, 0.01228],
                         # calibration = [9.49484, 0, 0, 201.5, 0.011742],
                         # curve from Vladimir Hutanu
                         # calibration = [7.67752, 239.074, 0.00822055, 6.14579, 0.913737],
                        ),

)
alias_config = {
    # I is included for the rare case you want to control the current directly instead of field.
    'B': {'B_ccmhts01': 100, 'I_ccmhts01': 90},
}
