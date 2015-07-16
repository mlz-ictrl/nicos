# -*- coding: utf-8 -*-

description = 'TOFTOF radial collimator'

group = 'optional'

includes = []

tango_host = 'tofhw.toftof.frm2:10000'

devices = dict(
    rc_onoff = device('devices.tango.NamedDigitalOutput',
                      description = 'Activates radial collimator',
                      tangodevice = 'tango://%s/toftof/rc/_rc_onoff' % tango_host,
                      mapping = {
                          'on': 1,
                          'off': 0,
                      },
                     ),

    rc_motor = device('devices.tango.AnalogOutput',
                      description = 'Radial collimator motor',
                      tangodevice = 'tango://%s/toftof/rc/_rc_motor' % tango_host,
                      lowlevel = True,
                     ),
)


startupcode = '''
'''
