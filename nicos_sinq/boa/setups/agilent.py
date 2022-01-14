description = 'Agilent frequency generator via EPICS'

pvprefix = 'SQ:BOA:AGILENT:'

devices = dict(
    amp = device('nicos.devices.epics.EpicsWindowTimeoutDevice',
        description = 'Amplitude of generated function in V.',
        readpv = pvprefix + 'AMP:RBV',
        writepv = pvprefix + 'AMP',
        precision = 0.1,
        window = 0.5,
        timeout = None,
        unit = 'V',
        abslimits = (-10, 10)
    ),
    freq = device('nicos.devices.epics.EpicsWindowTimeoutDevice',
        description = 'Frequency of generated function in Hz.',
        readpv = pvprefix + 'FREQ:RBV',
        writepv = pvprefix + 'FREQ',
        precision = 10,
        window = 0.5,
        timeout = None,
        unit = 'Hz',
        abslimits = (0, 200000)
    ),
    offset = device('nicos.devices.epics.EpicsWindowTimeoutDevice',
        description = 'Offset of generated function in volts.',
        readpv = pvprefix + 'OFF:RBV',
        writepv = pvprefix + 'OFF',
        precision = 0.001,
        window = 0.5,
        timeout = None,
        unit = 'deg',
        abslimits = (0, 5)
    ),
    phase = device('nicos.devices.epics.EpicsWindowTimeoutDevice',
        description = 'Phase shift of generated function in degrees.',
        readpv = pvprefix + 'PHASE:RBV',
        writepv = pvprefix + 'PHASE',
        precision = 0.001,
        window = 0.5,
        timeout = None,
        unit = 'deg',
        abslimits = (0, 360)
    ),
)
