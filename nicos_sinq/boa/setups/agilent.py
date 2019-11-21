description = 'Agilent frequency generator via EPICS'

pvprefix = 'SQ:BOA:AGILENT:'

devices = dict(
    amp = device('nicos.devices.epics.EpicsWindowTimeoutDevice',
        description = 'Amplitude of generated function in V.',
        readpv = pvprefix + 'AMP:RBV',
        writepv = pvprefix + 'AMP',
        precision = 0.001,
        window = 0.5,
        timeout = None,
        unit = 'V'
    ),
    freq = device('nicos.devices.epics.EpicsWindowTimeoutDevice',
        description = 'Frequency of generated function in Hz.',
        readpv = pvprefix + 'FREQ:RBV',
        writepv = pvprefix + 'FREQ',
        precision = 0.000001,
        window = 0.5,
        timeout = None,
        unit = 'Hz'
    ),
    phase = device('nicos.devices.epics.EpicsWindowTimeoutDevice',
        description = 'Phase shift of generated function in degree.',
        readpv = pvprefix + 'PHASE:RBV',
        writepv = pvprefix + 'PHASE',
        precision = 0.001,
        window = 0.5,
        timeout = None,
        unit = 'deg'
    ),
)
