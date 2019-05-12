description = 'vsd readout devices'

group = 'lowlevel'

devices = dict(
    User2Current = device('nicos.devices.generic.ManualMove',
        description = 'VSD: Analog value of User2Current',
        abslimits = (4, 20),
        unit = 'mA',
    ),
    User2Voltage = device('nicos.devices.generic.ManualMove',
        description = 'VSD: Analog value of User2Voltage',
        abslimits = (0, 10),
        unit = 'V',
    ),
    VSD_User2DigitalInput = device('nicos.devices.generic.ManualSwitch',
        description = 'VSD: Digital value of VSD_User2DigitalInput',
        states = ('On', 'Off'),
    ),
)
