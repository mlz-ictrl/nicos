description = 'Philipps Polarizer Setup'

group = 'optional'

includes = []


devices = dict(
    sry_polarizer = device('devices.taco.Motor',
                           description = 'Polarizer Rotation around Y',
                           tacodevice = 'antares/copley/m09',
                           abslimits = (-999999, 999999),
                          ),

    stx_polarizer = device('devices.taco.Motor',
                           description = 'Polarizer Translation X',
                           tacodevice = 'antares/copley/m10',
                           abslimits = (-99999, 99999),
                          ),
)

startupcode = '''
'''
