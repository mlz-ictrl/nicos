description = 'HERMES laser'
group = 'optional'

tango_base = 'tango://phys.hermes.jcns.fz-juelich.de:10000/hermes/'

devices = dict(
    laser = device('nicos.devices.entangle.NamedDigitalOutput',
        tangodevice = tango_base + 'euromove_motor/laser',
        description = 'Laser transversal translation.',
        mapping = {'in': 1010, 'out': 1030},
    ),
)
