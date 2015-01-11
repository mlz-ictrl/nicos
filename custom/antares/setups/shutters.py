# -*- coding: utf-8 -*-
description = 'ANTARES shutter devices'

group = 'optional'

includes = []

tango_host = 'tango://cpci01.antares.frm2:10000'

devices = dict(
    # Pilz shutter control
    shutter1_io = device('devices.tango.DigitalOutput',
                         description = 'Tango device for Shutter 1',
                         tangodevice = '%s/antares/fzjdp_digital/PilzShutter1' % tango_host,
                         lowlevel = True,
                        ),
    shutter1 = device('devices.generic.Switcher',
                      description = 'Shutter 1',
                      moveable = 'shutter1_io',
                      mapping = dict( open=1, closed=2 ),
                      fallback = '<undefined>',
                      precision = 0,
                     ),

    shutter2_io = device('devices.tango.DigitalOutput',
                         description = 'Tango device for Shutter 2',
                         tangodevice = '%s/antares/fzjdp_digital/PilzShutter2' % tango_host,
                         lowlevel = True,
                        ),
    shutter2 = device('devices.generic.Switcher',
                      description = 'Shutter 2',
                      moveable = 'shutter2_io',
                      mapping = dict( open=1, closed=2 ),
                      fallback = '<undefined>',
                      precision = 0,
                     ),

    fastshutter_io = device('devices.tango.DigitalOutput',
                            description = 'Tango device for Fast shutter',
                            tangodevice = '%s/antares/fzjdp_digital/FastShutter' % tango_host,
                            lowlevel = True,
                           ),
    fastshutter = device('devices.generic.Switcher',
                         description = 'Fast shutter',
                         moveable = 'fastshutter_io',
                         mapping = dict( open=1, closed=2 ),
                         fallback = '<undefined>',
                         precision = 0,
                        ),
)


startupcode = '''
'''
