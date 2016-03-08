# -*- coding: utf-8 -*-
description = 'ANTARES shutter devices'

group = 'optional'

includes = []

tango_base = 'tango://slow.antares.frm2:10000/antares/'

devices = dict(
    # Pilz shutter control
    shutter1_io = device('devices.tango.DigitalOutput',
                         description = 'Tango device for Shutter 1',
                         tangodevice = tango_base + 'fzjdp_digital/PilzShutter1',
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
                         tangodevice = tango_base + 'fzjdp_digital/PilzShutter2',
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
                            tangodevice = tango_base + 'fzjdp_digital/FastShutter',
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
