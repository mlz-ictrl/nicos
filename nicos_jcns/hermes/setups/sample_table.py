description = 'HERMES sample table'
group = 'optional'
display_order = 3

tango_base = 'tango://phys.hermes.jcns.fz-juelich.de:10000/hermes/'

devices = dict(
    sz = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'euromove_motor/sz',
        description = 'Sample table vertical translation.',
    ),
    sx = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'euromove_motor/sx',
        description = 'Sample table transversal translation.',
    ),
    sphi = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'euromove_motor/sphi',
        description = 'Sample table axis rotation.',
    ),
    sbk = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'euromove_motor/sbk',
        description = 'Anti-background slit vertical translation.',
    ),
    srho = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'euromove_motor/srho',
        description = 'Sample table rotation.',
    ),
    stheta = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'euromove_motor/stheta',
        description = 'Sample table rotation.',
    ),
)
