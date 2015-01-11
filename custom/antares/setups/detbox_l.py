description = 'Motor for FOV camera translation in large detector box'

group = 'optional'

includes = []

devices = dict(
    ccdtx = device('devices.taco.Motor',
                   description = 'Camera Translation X',
                   tacodevice = 'antares/copley/m06',
                   abslimits = (-9999, 9999),
                   userlimits = (-0, 693),
                  ),
)

startupcode = '''
'''
