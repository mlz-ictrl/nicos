description = 'Neutron counter box and HM at SINQ ZEBRA'

group = 'lowlevel'

includes = ['hm_config']

excludes = [
    'detector_single',
    'detector_single_v2',
    'detector_2d',
]

sysconfig = dict(datasinks = ['nxsink'])

pvprefix = 'SQ:ZEBRA:counter'

channels = ['monitorval', 'protoncurr']

devices = dict(
    elapsedtime = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQTime',
        daqpvprefix = pvprefix,
    ),
    monitorval = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor for neutron beam',
        daqpvprefix = pvprefix,
        channel = 1,
        type = 'monitor',
    ),
    protoncurr = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor for proton current',
        daqpvprefix = pvprefix,
        channel = 4,
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
    Gate1 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQGate',
        daqpvprefix = pvprefix,
        channel = 1,
        visibility = {'metadata', 'namespace'},
    ),
    Gate2 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQGate',
        daqpvprefix = pvprefix,
        channel = 2,
        visibility = {'metadata', 'namespace'},
    ),
    histogrammer = device('nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description = "Histogram Memory Channel",
        connector = 'hm_connector'
    ),
    area_detector = device('nicos_sinq.zebra.devices.zebrachannel.ZebraChannel',
        description = "Image channel for area detector",
        bank = 'hm_bank0',
        connector = 'hm_connector',
    ),
    zebradet = device(
        'nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'Detector device that counts neutrons and '
        'starts streaming events',
        timers = ['elapsedtime'],
        counters = [],
        monitors = ['DAQPreset'] + channels,
        images = ['area_detector'],
        others = ['histogrammer'],
        liveinterval = 20,
        saveintervals = [60]
    ),
    nxsink = device('nicos.nexus.NexusSink',
        description = "Sink for NeXus file writer",
        filenametemplate = ['zebra%(year)sn%(scancounter)06d.hdf'],
        templateclass =
        'nicos_sinq.zebra.nexus.nexus_templates.ZEBRATemplateProvider',
    ),
)

startupcode = '''
SetDetectors(zebradet)
Exp._setROParam('forcescandata', True)
'''
