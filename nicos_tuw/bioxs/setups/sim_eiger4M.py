description = 'Dectris Eiger2 4M'
group = 'lowlevel'

includes = ['filesavers']
excludes = ['eiger4M']

devices = dict(
    # Detector
    eiger = device('nicos.devices.generic.VirtualImage',
        description = 'Dectris Eiger2 4M',
        size = (2048, 2048)
    ),
    timer_eiger = device('nicos.devices.generic.VirtualTimer',
        description = "The camera's internal timer",

    ),
    det_eiger = device('nicos.devices.generic.Detector',
        description = 'Dectris Eiger2 4M',
        images = ['eiger'],
        timers = ['timer_eiger'],
    ),
    # MOTORS
    # Height
    detz_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample translation y-Axis motor',
        abslimits = (-10, 10),
        speed = 10,
        unit = 'mm',
        visibility = (),
    ),
    detz = device('nicos.devices.generic.Axis',
        description = 'Detector translation y-Axis motor',
        motor = 'detz_m',
        precision = 0.001,
    ),
    # distance
    dety_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Detector translation z-Axis motor',
        abslimits = (0, 700),
        speed = 10,
        unit = 'mm',
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
