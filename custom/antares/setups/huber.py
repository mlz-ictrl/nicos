description = 'HUBER Sample Table Experimental Chamber 1'

group = 'optional'

includes = ['alias_sample']

devices = dict(
    stx_huber = device('devices.taco.Motor',
                        description = 'Sample Translation X',
                        tacodevice = 'antares/copley/m01',
                        abslimits = (0, 400),
                      ),
    sty_huber = device('devices.taco.Motor',
                        description = 'Sample Translation X',
                        tacodevice = 'antares/copley/m02',
                        abslimits = (0, 400),
                      ),
    sgx       = device('devices.taco.Motor',
                        description = 'Sample Rotation around X',
                        tacodevice = 'antares/copley/m03',
                        abslimits = (-5, 5),
                      ),
    sgz       = device('devices.taco.Motor',
                        description = 'Sample Rotation around Z',
                        tacodevice = 'antares/copley/m04',
                        abslimits = (-5, 5),
                      ),
    sry_huber = device('devices.taco.Motor',
                        description = 'Sample Rotation around Y',
                        tacodevice = 'antares/copley/m05',
                        abslimits = (-999999, 999999),
                      ),
)

startupcode = '''
stx.alias = 'stx_huber'
sty.alias = 'sty_huber'
sry.alias = 'sry_huber'
'''
