# -*- coding: utf-8 -*-

description = 'Andor Neo sCMOS camera'

group = 'optional'

includes = ['shutters', 'filesavers']

tango_base = 'tango://antaresccd02.antares.frm2:10000/antares/'

devices = dict(
    neo = device('antares.detector.AntaresNeo',
                 description = 'The Andor Neo sCMOS camera detector',
                 tangodevice = tango_base + 'detector/limaccd',
                 hwdevice = tango_base + 'detector/neo',
                 fastshutter = 'fastshutter',
                 pollinterval = 3,
                 maxage = 9,
                 flip = (False, True),
                 rotation = 90,
                 subdir = '.',
                 fileformats = ['FITSFileSaver'],
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
)

startupcode = '''
SetDetectors(neo)

## override hw setting to known good values.
neo.rotation = 90
'''
