description = 'Sample table devices'

group = 'lowlevel'

tango_base = 'tango://motorbox02.erwin.frm2.tum.de:10000/box/'

devices = dict(
    xs = device('nicos.devices.generic.Axis',
        description = 'X translation',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'channel1/motor',
        ),
        precision = 0.01,
    ),
    ys = device('nicos.devices.generic.Axis',
        description = 'Y translation',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'channel2/motor',
        ),
        precision = 0.01,
    ),
    zs = device('nicos.devices.generic.Axis',
        description = 'Z translation',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'channel3/motor',
        ),
        coder = device('nicos.devices.entangle.Sensor',
            tangodevice = tango_base + 'channel3/encoder',
        ),
        precision = 0.01,
    ),
    omgs = device('nicos.devices.generic.Axis',
        description = 'Omega of sample',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'channel4/motor',
        ),
        coder = device('nicos.devices.entangle.Sensor',
            tangodevice = tango_base + 'channel4/encoder',
        ),
        precision = 0.01,
    ),
    tths = device('nicos.devices.generic.Axis',
        description = '2theta of sample',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'channel6/motor',
        ),
        coder = device('nicos.devices.entangle.Sensor',
            tangodevice = tango_base + 'channel6/encoder',
        ),
        precision = 0.01,
    ),
    tths2 = device('nicos.devices.generic.Axis',
        description = '2theta of sample',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'channel5/motor',
        ),
        coder = device('nicos.devices.entangle.Sensor',
            tangodevice = tango_base + 'channel5/encoder',
        ),
        precision = 0.01,
    ),
)