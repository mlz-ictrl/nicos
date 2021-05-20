description = 'Setup for the picoscope flipper'

devices = dict(
    pico_amp = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Spin Flipper Amplitude',
        writepv = 'SQ:BOA:pico:AMP',
        readpv = 'SQ:BOA:pico:AMP_RBV',
        window = .1,
        abslimits = (-10, 10)
    ),
    pico_freq = device('nicos_sinq.devices.epics.generic.WindowMoveable',
        description = 'Spin Flipper Frequency',
        writepv = 'SQ:BOA:pico:FREQ',
        readpv = 'SQ:BOA:pico:FREQ_RBV',
        abslimits = (0, 300000),
        window = 1
    ),
    pico_onoff = device('nicos.devices.epics.EpicsWindowTimeoutDevice',
        description = 'Spin Flipper On/Off (On = 0, Off = 1)',
        writepv = 'SQ:BOA:pico:ONOFF',
        readpv = 'SQ:BOA:pico:ONOFF_RBV',
        abslimits = (0, 1),
        window = 1,
        timeout = 20,
        precision = 0.1,
    ),
)
