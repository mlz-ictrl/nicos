description = 'Neutron Grating Interferometer'

group = 'optional'

tango_host = 'phytron3.antareslab'

tango_base = f'tango://{tango_host}:10000/box/'

devices = dict(
    sry = device('nicos.devices.entangle.Motor',
        speed = 5,
        unit = 'deg',
        description = 'Sample rotation',
        tangodevice = tango_base + 'phytron5/mot',
        userlimits = (-999, 999),
        maxage = 5,
        pollinterval = 3,
        precision = 0.001,
    ),
    stx = device('nicos.devices.entangle.Motor',
        speed = 2.5,
        unit = 'mm',
        description = 'Sample translation x',
        tangodevice = tango_base + 'phytron6/mot',
        userlimits = (-999, 999),
        maxage = 5,
        pollinterval = 3,
        precision = 0.01,
    ),
    focus = device('nicos.devices.entangle.Motor',
        speed = 100,
        unit = 'deg',
        description = 'focus rotation',
        tangodevice = tango_base + 'phytron7/mot',
        userlimits = (-999999, 999999),
        maxage = 5,
        pollinterval = 3,
        precision = 0.1,
    ),
    scintillatortz = device('nicos.devices.entangle.Motor',
        speed = 100,
        unit = 'um',
        description = 'Translation of scintillator for microscope setup',
        tangodevice = tango_base + 'phytron4/mot',
        userlimits = (-12500, 12500),
        maxage = 5,
        pollinterval = 3,
        precision = 0.1,
    ),

)

