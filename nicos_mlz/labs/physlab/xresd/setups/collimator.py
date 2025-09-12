description = 'Devices to adjust collimator'

group = 'lowlevel'

tango_base = 'tango://rsxrd.physlab.frm2.tum.de:10000/box/mcc1/'

devices = dict(
    m1 = device('nicos.devices.entangle.Motor',
        description = 'Motor 1 of the collimator alignment stage',
        tangodevice = tango_base + 'motor1',
    ),
    m2 = device('nicos.devices.entangle.Motor',
        description = 'Motor 2 of the collimator alignment stage',
        tangodevice = tango_base + 'motor2',
    ),
)
