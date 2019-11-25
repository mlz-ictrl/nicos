# -*- coding: utf-8 -*-

description = 'Andor DV434 CCD camera'

group = 'optional'

includes = ['filesavers']

tango_base = 'tango://nectarccd02.nectar.frm2:10000/nectar/'

devices = dict(
    timer = device('nicos.devices.vendor.lima.LimaCCDTimer',
        description = 'The camera\'s internal timer',
        tangodevice = tango_base + 'detector/limaccd',
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'The Andor Neo sCMOS camera detector',
        images = ['ccd'],
        timers = ['timer'],
    ),
    ccd = device('nicos.devices.vendor.lima.Andor2LimaCCD',
        description = 'The CCD detector',
        tangodevice = tango_base + 'detector/limaccd',
        hwdevice = tango_base + 'detector/dv434',
        pollinterval = 5,
        maxage = 12,
        flip = (False, False),
        rotation = 0,
        shutteropentime = 0.05,
        shutterclosetime = 0.05,
        shuttermode = 'auto',
        vsspeed = 16.0,
        hsspeed = 1,
        pgain = 1,
    ),
    ccdTemp = device('nicos.devices.vendor.lima.Andor2TemperatureController',
        description = 'Temperature of the CCD detector',
        tangodevice = tango_base + 'detector/dv434',
        pollinterval = 5,
        maxage = 12,
        abslimits = (-100, 0),
        userlimits = (-100, 0),
        unit = 'degC',
        precision = 3,
        fmtstr = '%.0f',
    ),
)

startupcode = '''
SetDetectors(det)

## override hw setting to known good values.
ccd.rotation = 0
ccd.shutteropentime = 0.05
ccd.shutterclosetime = 0.05
ccd.shuttermode = 'auto'
ccd.vsspeed = 16.0
ccd.hsspeed = 1
ccd.pgain = 1
'''
