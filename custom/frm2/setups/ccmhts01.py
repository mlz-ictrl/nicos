description = 'High-Tc superconducting magnet'

group = 'plugplay'

includes = ['alias_B']

taco_host = 'ccmhts01'

devices = dict(
    # by convention this needs to be B_%(setupname)s
    B_ccmhts01  = device('devices.taco.CurrentSupply',
                         description = 'magnetic field device',
                         tacodevice = '//%s/magnet/kepco/current' % taco_host,
                         unit = 'A',
                         abslimits = (-210, 210),
                        ),
)

startupcode = '''
B.alias = B_ccmhts01
'''
