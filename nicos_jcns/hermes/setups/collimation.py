description = 'HERMES collimation system'
group = 'optional'
display_order = 2

tango_base = 'tango://phys.hermes.jcns.fz-juelich.de:10000/hermes/'

devices = dict(
    m1theta = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'euromove_motor/m1theta',
        description = 'Collimator 1 mirror rotation.',
    ),
    m1z = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'euromove_motor/m1z',
        description = 'Collimator 1 mirror vertical translation.',
    ),
    m2theta = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'euromove_motor/m2theta',
        description = 'Collimator 2 mirror rotation.',
    ),
    m2z = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'euromove_motor/m2z',
        description = 'Collimator 2 vertical translation.',
    ),
)
