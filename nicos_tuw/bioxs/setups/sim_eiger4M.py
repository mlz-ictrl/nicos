description = 'Dectris Eiger2 4M'
group = 'lowlevel'

includes = ['filesavers']
excludes = ['eiger4M']

devices = dict(
    # Detector
    seiger = device('nicos.devices.generic.VirtualImage',
        description = 'Dectris Eiger2 4M',
        size = (2048, 2048)
    ),
    stimer_eiger = device('nicos.devices.generic.VirtualTimer',
        description = "The camera's internal timer",

    ),
    sdet_eiger = device('nicos.devices.generic.Detector',
        description = 'Dectris Eiger2 4M',
        images = ['seiger'],
        timers = ['stimer_eiger'],
    ),
    # MOTORS
    # Height
    sdetz_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample translation y-Axis motor',
        abslimits = (-10, 10),
        speed = 10,
        unit = 'mm',
        visibility = (),
    ),
    sdetz = device('nicos.devices.generic.Axis',
        description = 'Detector translation y-Axis motor',
        motor = 'sdetz_m',
        precision = 0.001,
    ),
    # distance
    sdety_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Detector translation z-Axis motor',
        abslimits = (0, 700),
        speed = 10,
        unit = 'mm',
        visibility = (),
    ),
    sdety = device('nicos.devices.generic.Axis',
        description = 'Detector translation z-Axis motor',
        motor = 'sdety_m',
        precision = 0.001,
    ),
)

startupcode = '''
SetDetectors(sdet_eiger)
'''
