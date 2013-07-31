description = 'Detector Table Experimental Chamber 1'

group = 'optional'

includes = []

devices = dict(
    dtx = device('devices.taco.Motor',
                        description = 'Detector Translation X',
                        tacodevice = 'antares/copley/m14',
                        abslimits = (0, 700),
                      ),
    dty = device('devices.taco.Motor',
                        description = 'Detector Translation X',
                        tacodevice = 'antares/copley/m15',
                        abslimits = (0, 380),
                      ),
)

startupcode = '''
'''
