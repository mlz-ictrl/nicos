# -*- coding: utf-8 -*-

description = 'Andor Neo sCMOS camera'

group = 'lowlevel'

tango_base = 'tango://localhost:10000/pgaa/'

devices = dict(
    timer_neo = device('nicos.devices.vendor.lima.LimaCCDTimer',
        description = 'The camera\'s internal timer',
        tangodevice = tango_base + 'detector/limaccd',
        lowlevel = True,
    ),
    neo = device('nicos.devices.vendor.lima.Andor3LimaCCD',
        description = 'Andor Neo sCMOS camera detector image',
        tangodevice = tango_base + 'detector/limaccd',
        hwdevice = tango_base + 'detector/neo',
        pollinterval = 3,
        maxage = 9,
        flip = (False, True),
        rotation = 90,
        readoutrate = 280,
        lowlevel = True,
    ),
    temp_neo = device('nicos.devices.vendor.lima.Andor3TemperatureController',
        description = 'The CMOS chip temperature',
        tangodevice = tango_base + 'detector/neo',
        maxage = 5,
        abslimits = (-100, 0),
        userlimits = (-100, 0),
        unit = 'degC',
        precision = 3,
        fmtstr = '%.0f',
    ),
    det_neo = device('nicos.devices.generic.Detector',
        description = 'The Andor Neo sCMOS camera detector',
        images = ['neo'],
        timers = ['timer_neo'],
    ),
)

startupcode = '''
SetDetectors(det_neo)

## override hw setting to known good values.
set('neo', 'rotation', 90)
'''

