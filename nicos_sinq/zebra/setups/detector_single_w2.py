description = 'Setup for the single detector at ZEBRA on Wagen 2'

includes = [
    'wagen2'
]

excludes = [
    'detector_single',
    'detector_2d',
]

sysconfig = dict(datasinks = ['asciisink', 'cclsink'])

pvprefix = 'SQ:ZEBRA:counter'

channels = ['counts', 'monitor1', 'protoncount']

devices = dict(
    elapsedtime = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQTime',
        daqpvprefix = pvprefix,
    ),
    counts = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Actual counts',
        daqpvprefix = pvprefix,
        channel = 4,
        type = 'monitor',
    ),
    monitor1 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'First scalar counter channel',
        daqpvprefix = pvprefix,
        channel = 1,
        type = 'monitor',
    ),
    protoncount = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Proton counter channel',
        daqpvprefix = pvprefix,
        channel = 3,
        type = 'monitor',
    ),
    hardware_preset = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQPreset',
        description = 'In-hardware Time/Count Preset',
        daqpvprefix = pvprefix,
        channels = channels,
        time_channel = 'elapsedtime',
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

    intensity = device('nicos_sinq.sxtal.commands.Intensity',
        description = 'Dummy to try to get stuff to work'
    ),
    zebradet = device('nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'EL737 counter box that counts neutrons',
        timers = ['elapsedtime'],
        monitors = ['hardware_preset'] + channels,
        images = [],
        others = [],
        liveinterval = 7,
        saveintervals = [60]
    ),
    asciisink = device('nicos_sinq.sxtal.datasink.SxtalScanSink',
        description = 'Sink for writing SINQ ASCII files',
        filenametemplate = ['zebra%(year)sn%(scancounter)06d.dat'],
        templatefile = 'nicos_sinq/zebra/zebra.hdd',
        visibility = (),
        scaninfo = [
            ('Counts', 'counts'), ('Monitor1', 'monitor1'),
            ('Proton', 'protoncount'), ('Time', 'elapsedtime')
        ]
    ),
    cclsink = device('nicos_sinq.sxtal.datasink.CCLSink',
        description = 'Sink for writing SINQ ASCII files',
        filenametemplate = ['zebra%(year)sn%(scancounter)06d.ccl'],
        templatefile = 'nicos_sinq/zebra/mess.hdd',
        visibility = (),
        detector = 'counts',
        scaninfo = [
            ('Counts', 'counts'), ('Monitor1', 'monitor1'),
            ('Proton', 'protoncount'), ('Time', 'elapsedtime')
        ]
    ),
)
startupcode = """
SetDetectors(zebradet)
Exp._setROParam('forcescandata', False)
stt.offset = 0
"""
