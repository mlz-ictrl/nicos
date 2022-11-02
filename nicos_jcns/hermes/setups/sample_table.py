description = 'HERMES sample table'
group = 'optional'
display_order = 3

tango_base = 'tango://phys.hermes.jcns.fz-juelich.de:10000/hermes/euromove/'

devices = dict(
    sz = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'sz',
        description = 'Sample table vertical translation.',
    ),
    sx = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'sx',
        description = 'Sample table transversal translation.',
    ),
    sphi = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'sphi',
        description = 'Sample table axis rotation.',
    ),
    sbk = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'sbk',
        description = 'Anti-background slit vertical translation.',
    ),
    srho = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'srho',
        description = 'Sample table rotation.',
    ),
    stheta = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'stheta',
        description = 'Sample table rotation.',
    ),
)
