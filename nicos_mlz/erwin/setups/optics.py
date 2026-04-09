description = 'Secondary collimator devices'

group = 'lowlevel'

tango_base = 'tango://motorbox01.erwin.frm2.tum.de:10000/box/'
# tango_base = ''

devices = dict(
    zo = device('nicos.devices.generic.Axis',
        description = 'Secondary collimator lift',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'channel4/motor',
        ),
        coder = device('nicos.devices.entangle.Sensor',
            tangodevice = tango_base + 'channel4/coder',
        ),
        precision = 0.05,
    ),
    # yo = device('nicos.devices.generic.Axis',
    #     description = 'Secondary collimator lift',
    #     motor = device('nicos.devices.entangle.Motor',
    #         tangodevice = tango_base + 'channel?/motor',
    #     ),
    #     coder = device('nicos.devices.entangle.Sensor',
    #         tangodevice = tango_base + 'channel?/coder',
    #     ),
    #     precision = 0.05,
    # ),
    xo = device('nicos.devices.generic.ManualMove',
        description = 'Secondary collimator X translation',
        abslimits = (0, 200),
        unit = 'mm',
    ),
)
