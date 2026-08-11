description = 'Sample slits'

group = 'lowlevel'

tango_base = 'tango://motorbox01.erwin.frm2.tum.de:10000/box/'

devices = dict(
    ssy = device('nicos.devices.generic.Axis',
        description = 'Y position of center of sample slit',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'channel1/motor',
            # abslimits = (-25, 25),
            unit = 'mm',
        ),
        precision = 0.01,
    ),
    ssz = device('nicos.devices.generic.Axis',
        description = 'Z position of center of sample slit',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'channel2/motor',
            # abslimits = (-25, 25),
            unit = 'mm',
        ),
        precision = 0.01,
    ),
)
