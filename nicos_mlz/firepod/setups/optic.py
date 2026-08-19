description = 'Optic devices'

group = 'lowlevel'

tango_base = 'tango://firepodhw.firepod.frm2.tum.de:10000/beckhoff/optic/_'

devices = dict(
    bs = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Beamstop selection device',
        tangodevice = tango_base + 'beamstop',
        mapping = {'down': 0, 'up': 1},
    ),
    collimator = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Collimator insert device',
        tangodevice = tango_base + 'collimator',
        mapping = {'out': 0, 'in': 1},
    ),
    filter = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Graphite filter device',
        tangodevice = tango_base + 'pg_filter',
        mapping = {'out': 0, 'in': 1},
    ),
    laser = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Adjustment laser device',
        tangodevice = tango_base + 'laser',
        mapping = {'out': 0, 'in': 1},
    ),
    shutter = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Instrument fast shutter',
        tangodevice = tango_base + 'shutter',
        mapping = {'closed': 0, 'open': 1},
    ),
)
