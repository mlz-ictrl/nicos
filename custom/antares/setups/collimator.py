# -*- coding: utf-8 -*-

description = 'ANTARES collimator drum'

group = 'optional'

includes = []

tango_host = 'tango://cpci01.antares.frm2:10000'

devices = dict(
    # Collimator
    collimator_io = device('devices.tango.DigitalOutput',
                           description = 'Tango device for Collimator',
                           tangodevice = '%s/antares/fzjdp/Collimator' % tango_host,
                           lowlevel = True,
                          ),
    collimator = device('devices.generic.Switcher',
                        description = 'Collimator, value is L/D',
                        moveable = 'collimator_io',
                        mapping = { 3200:1, 200:2, 800:3, 7100:4, 400:5, 1600:6, 'park':7, },
                        fallback = '<undefined>',
                        unit = 'L/D',
                        precision = 0,
                       ),

)


startupcode = '''
'''
