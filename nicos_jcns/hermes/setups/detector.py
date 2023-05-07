description = 'HERMES detector alignment'
group = 'optional'
display_order = 4

tango_base = 'tango://phys.hermes.jcns.fz-juelich.de:10000/hermes/'

devices = dict(
    detangle = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'euromove_motor/detangle',
        description = 'Detector angle.',
        requires = dict(level='admin'),
        visibility = (),
    ),
    detz = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'euromove_motor/detz',
        description = 'Detector vertical translation.',
    ),
)
