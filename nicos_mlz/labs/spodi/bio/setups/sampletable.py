description = 'Sample table devices'

setup = 'optional'

tango_base = 'tango://motorbox10.spodi.frm2.tum.de:10000/box/omgs/'

devices = dict(
    omgs_motor = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'motor',
        visibility = (),
    ),
    omgs_coder = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'encoder',
        visibility = (),
    ),
    omgs = device('nicos.devices.generic.Axis',
        description = 'Omega sample rotation',
        motor = 'omgs_motor',
        coder = 'omgs_coder',
        precision = 0.01,
    ),
)
