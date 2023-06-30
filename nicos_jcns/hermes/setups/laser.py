description = 'HERMES laser'
group = 'optional'

tango_base = 'tango://phys.hermes.jcns.fz-juelich.de:10000/hermes/'

devices = dict(
    laser = device('nicos_jcns.hermes.devices.laser.Motor',
        description = 'Laser transversal translation.',
        tangodevice = tango_base + 'euromove_motor/laser',
        visibility = (),
    ),
    laser_switcher = device('nicos.devices.generic.switcher.Switcher',
        description = 'Switcher that moves the laser in and out.',
        mapping = {'in': 50.0, 'out': 0.0},
        moveable = 'laser',
        precision = 0.1,
    ),
)
