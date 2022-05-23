# -*- coding: utf-8 -*-

description = 'Andor Neo sCMOS camera'

group = 'optional'

includes = ['filesavers']

tango_base = 'tango://192.168.20.33:10000/antares/'

devices = dict(
    fastshutter_io = device('nicos.devices.generic.manual.ManualSwitch',
        description = 'fake fast shutter',
        states = [1, 2,
                  ],
    ),
    fastshutter = device('nicos.devices.generic.Switcher',
        description = 'Fast shutter',
        moveable = 'fastshutter_io',
        mapping = dict(open = 1, closed = 2),
        fallback = '<undefined>',
        precision = 0,
        unit = '',
    ),
    timer_neo = device('nicos.devices.vendor.lima.LimaCCDTimer',
        description = 'The camera\'s internal timer',
        tangodevice = tango_base + 'detector/limaccd',
    ),
    neo = device('nicos_mlz.antares.devices.detector.AntaresNeo',
        description = 'Andor Neo sCMOS camera detector image',
        tangodevice = tango_base + 'detector/limaccd',
        hwdevice = tango_base + 'detector/neo',
        fastshutter = 'fastshutter',
        pollinterval = 3,
        maxage = 9,
        flip = (False, True),
        rotation = 90,
        openfastshutter = False,
        readoutrate = 280,
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
    sharpness = device('nicos_mlz.antares.devices.detector.Sharpness',
        description = 'Sharpness signal from the detector image'
    ),
    det_sharp = device('nicos.devices.generic.Detector',
        description = 'The Andor Neo sCMOS camera detector with sharpness signal',
        images = ['neo'],
        timers = ['timer_neo'],
        counters = ['sharpness'],
        postprocess = [('sharpness', 'neo')],
    ),
)

startupcode = '''
SetDetectors(det_neo)

## override hw setting to known good values.
neo.rotation = 90
'''
