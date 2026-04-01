description = 'Base setup file for ORION devices'

group = 'lowlevel'
pvdet = 'SQ:ORION:DAQ'

channels = [ 'monitor1', 'counts', 'protoncount' ]

devices = dict(
    elapsedtime = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQTime',
        daqpvprefix = pvdet,
    ),
    DAQPreset = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQPreset',
        description = '1st Generation Data Acquisition',
        daqpvprefix = pvdet,
        time_channel = 'elapsedtime',
        channels = channels,
    ),
    ThresholdChannel = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThresholdChannel',
        daqpvprefix = pvdet,
        channels = channels,
    ),
    Threshold = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThreshold',
        daqpvprefix = pvdet,
        min_rate_channel = 'ThresholdChannel',
    ),
    intensity = device('nicos_sinq.sxtal.commands.Intensity',
        description = 'Dummy to try to get stuff to work'
    ),
    monitor1 = device('nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'First scalar counter channel',
        type = 'monitor',
        channel = 1,
        daqpvprefix = pvdet,
    ),
    counts = device('nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Actual counts',
        type = 'monitor',
        channel = 2,
        daqpvprefix = pvdet,
    ),
    protoncount = device('nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Proton counter channel',
        type = 'monitor',
        channel = 4,
        daqpvprefix = pvdet,
    ),
    oriondet = device(
        'nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'EL737 counter box that counts neutrons and starts streaming events',
        timers = ['elapsedtime'],
        monitors = ['DAQPreset'] + channels,
        counters = [],
        liveinterval = 7,
        saveintervals = [60]
    ),
)

startupcode = """
SetDetectors(oriondet)
"""
