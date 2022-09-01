description = 'vsd readout devices'

group = 'lowlevel'

devices = dict(
    User2Current = device('nicos.devices.generic.ManualMove',
        description = 'VSD: Analog value of User2Current',
        abslimits = (4, 20),
        default = 5,
        unit = 'mA',
    ),
    User2Voltage = device('nicos.devices.generic.ManualMove',
        description = 'VSD: Analog value of User2Voltage',
        abslimits = (0, 10),
        default = 5,
        unit = 'V',
    ),
    VSD_User2DigitalInput = device('nicos.devices.generic.ManualMove',
        description = 'VSD: Digital value of VSD_User2DigitalInput',
        abslimits = (0, 10),
        default = 1,
        unit = 'V',
    ),
)
