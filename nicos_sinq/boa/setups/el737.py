description = 'EL737 Sinq Counterbox Common Config'

group = 'lowlevel'

pvprefix = 'SQ:BOA:counter'

channels = ['monitorval', 'protoncurr']

devices = dict(
    elapsedtime = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQTime',
        daqpvprefix = pvprefix,
    ),
    protoncurr = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor for proton current',
        daqpvprefix = pvprefix,
        channel = 3,
        type = 'monitor',
    ),
    monitorval = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor for Neutron Beam',
        daqpvprefix = pvprefix,
        channel = 1,
        type = 'monitor',
    ),
    ThresholdChannel = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThresholdChannel',
        daqpvprefix = pvprefix,
        channels = channels,
        visibility = {'metadata', 'namespace'},
    ),
    Threshold = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThreshold',
        daqpvprefix = pvprefix,
        min_rate_channel = 'ThresholdChannel',
        visibility = {'metadata', 'namespace'},
    ),
    hardware_preset = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQPreset',
        description = 'In-hardware Time/Count Preset',
        daqpvprefix = pvprefix,
        channels = channels,
        time_channel = 'elapsedtime',
    ),
)
