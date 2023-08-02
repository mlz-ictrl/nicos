description = 'Setup for the picoscope flipper switched through the MCU'

devices = dict(
    pico_onoff = device('nicos.devices.epics.pyepics.EpicsWindowTimeoutDevice',
        description = 'Spin Flipper On/Off (On = 0, Off = 1)',
        writepv = 'SQ:BOA:pico:ONOFF',
        readpv = 'SQ:BOA:pico:ONOFF_RBV',
        abslimits = (0, 1),
        window = 1,
        timeout = 20,
        precision = 0.1,
    ),
    mcu2 = device('nicos_sinq.devices.epics.extensions.EpicsCommandReply',
        description = 'Controller of the devices connected to MCU2',
        commandpv = 'SQ:BOA:MCU2.AOUT',
        replypv = 'SQ:BOA:MCU2.AINP',
    ),
    pico_mcu = device('nicos_sinq.boa.devices.pico.PicoSwitch',
        description = 'Device to switch flipper via MCU',
        directmcu = 'mcu2',
        mapping = {
            'on': 1,
            'off': 0
        },
    )
)
