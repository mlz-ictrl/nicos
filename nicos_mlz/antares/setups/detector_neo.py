description = 'Andor Neo sCMOS camera'
group = 'optional'

includes = ['shutters', 'filesavers']

tango_base = 'tango://antaresccd02.antares.frm2.tum.de:10000/antares/'

devices = dict(
    timer_neo = device('nicos.devices.vendor.lima.LimaCCDTimer',
        description = 'The camera\'s internal timer',
        tangodevice = tango_base + 'detector/limaccd',
    ),
    neo = device('nicos_mlz.antares.devices.detector.Neo',
        description = 'Andor Neo sCMOS camera detector image',
        tangodevice = tango_base + 'detector/limaccd',
        hwdevice = tango_base + 'detector/neo',
        fastshutter = 'fastshutter',
        pollinterval = 3,
        maxage = 9,
        flip = (False, True),
        rotation = 90,
        openfastshutter = True,
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
    socket_neo = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Power socket 01 (Neo Camera attached)',
        tangodevice = 'tango://antareshw.antares.frm2.tum.de:10000/antares/'
        'fzjdp_digital/Socket01',
        mapping = dict(on = 1, off = 0),
    )
)

startupcode = '''
SetDetectors(det_neo)

## override hw setting to known good values.
neo.rotation = 90
'''
