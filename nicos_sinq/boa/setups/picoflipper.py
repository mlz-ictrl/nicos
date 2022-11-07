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
)
