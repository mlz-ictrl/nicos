description = 'collimator setup for tension scanner'

group = 'lowlevel'

excludes = ['collimator']

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    collimator_m=device('nicos.devices.entangle.Motor',
                        description='tango device for collimator',
                        tangodevice=tango_base + 'collimator/motor',
                        userlimits=(270, 270),
                        visibility=(),
                        ),
    hole=device('nicos.devices.generic.Switcher',
                description='hole',
                moveable='collimator_m',
                mapping={
                    'open': 270,
                },
                precision=0.01,
                fmtstr='%.2f',
                requires={'level': 'admin'},
                ),
)

startupcode = '''
maw(hole, 'open')
'''
