description = 'Devices for the spin flipper at SANS, implemented with a HAMEG 8131'

pvprefix = 'SQ:SANS:flip'

devices = dict(
    flip_freq = device('nicos.devices.epics.EpicsAnalogMoveable',
        description = 'Set frequency',
        readpv = pvprefix + ':FREQ_RBV',
        writepv = pvprefix + ':FREQ',
        abslimits = (100E-6, 15E06),
        precision = 5.,
        monitor = True
    ),
    flip_amp = device('nicos.devices.epics.EpicsAnalogMoveable',
        description = 'Set amplitude',
        readpv = pvprefix + ':AMP_RBV',
        writepv = pvprefix + ':AMP',
        abslimits = (20E-3, 20.),
        precision = .01,
        monitor = True
    ),
    flip_off = device('nicos.devices.epics.EpicsAnalogMoveable',
        description = 'Set offset',
        readpv = pvprefix + ':OFF_RBV',
        writepv = pvprefix + ':OFF',
        abslimits = (-5, 5),
        precision = .1,
        monitor = True
    ),
    flip_state = device('nicos.devices.epics.EpicsMappedMoveable',
        description = 'Set state, on/off',
        readpv = pvprefix + ':STATE_RBV',
        writepv = pvprefix + ':STATE',
        ignore_stop = True,
        monitor = True
    ),
)
