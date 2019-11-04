# -*- coding: utf-8 -*-

description = 'Andor Neo sCMOS camera'

group = 'optional'

includes = ['shutters', 'filesavers']

devices = dict(
    timer_neo = device('nicos.devices.generic.VirtualTimer',
        description = 'The camera\'s internal timer',
    ),
    neo = device('nicos.devices.generic.VirtualImage',
        description = 'Andor Neo sCMOS camera detector image',
        sizes = (1024, 1024),
    ),
    temp_neo = device('nicos.devices.generic.VirtualTemperature',
        description = 'The CMOS chip temperature',
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
'''
