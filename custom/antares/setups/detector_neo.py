# -*- coding: utf-8 -*-

description = 'Andor Neo sCMOS camera'

group = 'optional'

includes = ['shutters', 'filesavers']

tango_base = 'tango://antaresccd02.antares.frm2:10000/antares/'

devices = dict(
    timer   = device('devices.vendor.lima.LimaCCDTimer',
                     description = 'The camera\'s internal timer',
                     tangodevice = tango_base + 'detector/limaccd',
                    ),

    neo     = device('antares.detector.AntaresNeo',
                     description = 'Andor Neo sCMOS camera detector image',
                     tangodevice = tango_base + 'detector/limaccd',
                     hwdevice = tango_base + 'detector/neo',
                     fastshutter = 'fastshutter',
                     pollinterval = 3,
                     maxage = 9,
                     flip = (False, True),
                     rotation = 90,
                     openfastshutter = False,
                    ),
    neoTemp = device('devices.vendor.lima.Andor3TemperatureController',
                     description = 'The CMOS chip temperature',
                     tangodevice = tango_base + 'detector/neo',
                     maxage = 5,
                     abslimits = (-100, 0),
                     userlimits = (-100, 0),
                     unit = 'degC',
                     precision = 3,
                     fmtstr = '%.0f',
                    ),

    det     = device('devices.generic.Detector',
                     description = 'The Andor Neo sCMOS camera detector',
                     images = ['neo'],
                     timers = ['timer'],
                     fileformats = ['FITSFileSaver'],
                    ),
)

startupcode = '''
SetDetectors(det)

## override hw setting to known good values.
neo.rotation = 90
'''
