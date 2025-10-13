description = 'Dectris Eiger2 4M'
group = 'lowlevel'

includes = ['filesavers']

tango_base_detector = 'tango://bioxs:10000/lima/'
tango_base_motor = 'tango://bioxs:10000/motor/'

devices = dict(
    # Detector
    eiger = device('nicos.devices.vendor.lima.EigerLimaCCD',
        description = 'Dectris Eiger2 4M',
        tangodevice = tango_base_detector + 'limaccd/1',
        hwdevice = tango_base_detector + 'limaccd/eiger',
    ),
    timer_eiger = device('nicos.devices.vendor.lima.LimaCCDTimer',
        description = "The camera's internal timer",
        tangodevice = tango_base_detector + 'limaccd/1',
    ),
    det_eiger = device('nicos.devices.generic.Detector',
        description = 'Dectris Eiger2 4M',
        images = ['eiger'],
        timers = ['timer_eiger'],
    ),
    # MOTORS
    # Height
    detz_m = device('nicos.devices.entangle.Motor',
        description = 'Sample translation y-Axis motor',
        tangodevice = tango_base_motor + 'phymotion/detz_motor',
        visibility = (),
    ),
    detz = device('nicos.devices.generic.Axis',
        description = 'Detector translation y-Axis motor',
        motor = 'detz_m',
        precision = 0.001,
    ),
    # distance
    dety_m = device('nicos.devices.entangle.Motor',
        description = 'Detector translation z-Axis motor',
        tangodevice = tango_base_motor + 'phymotion/dety_motor',
        visibility = (),
    ),
    dety = device('nicos.devices.generic.Axis',
        description = 'Detector translation z-Axis motor',
        motor = 'dety_m',
        precision = 0.001,
    ),
)

startupcode = '''
SetDetectors(det_eiger)
'''
