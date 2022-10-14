description = 'collimator setup for the other modes of operation'

group = 'lowlevel'

excludes = ['collimator_2']

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    collimator_m=device('nicos.devices.entangle.Motor',
                        description='tango device for collimator',
                        tangodevice=tango_base + 'collimator/motor',
                        userlimits=(0, 180),
                        visibility=(),
                        ),
    hole=device('nicos.devices.generic.Switcher',
                description='hole',
                moveable='collimator_m',
                mapping={
                    'Soller #1': 0,
                    'Soller #2': 90,
                    'Soller #3': 180,
                },
                precision=0.01,
                fmtstr='%.2f',
                requires={'level': 'admin'},
                ),
)

startupcode = '''
maw(hole, 'Soller #1')
'''
