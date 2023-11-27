description = 'Collimator and filter changers'

group = 'lowlevel'

tango_base = 'tango://erwinhw.erwin.frm2.tum.de:10000/erwin/'

devices = dict(
    filter = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Filter changing device',
        tangodevice = tango_base + 'filter/out',
        mapping = {
            'in': 1,
            'out': 0,
        },
    ),
    collimator = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Collimator changing device',
        tangodevice = tango_base + 'collimator/out',
        mapping = {
            'in': 1,
            'out': 0,
        },
    ),
)
