description = 'Setup for the CAMEA detector'

group = 'basic'

display_order = 50

sysconfig = dict(
    datasinks = ['nxsink'],
)

includes = ['mono_slit', 'cameabasic', 'hm_config'] # The real thing
#includes=['mono_slit', 'cameabasic', 'hm_config_sim'] # For simulation
excludes = ['andorccd', 'detector_old']

countprefix = 'SQ:CAMEA:counter'

devices = dict(
    nxsink = device('nicos.nexus.NexusSink',
        description = 'Sink for NeXus file writer',
        filenametemplate = ['camea%(year)sn%(scancounter)06d.hdf'],
        templateclass = 'nicos_sinq.camea.nexus.nexus_templates'
        '.CameaTemplateProvider',
    ),
    elapsedtime = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQTime',
        daqpvprefix = countprefix,
    ),
    DAQPreset = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQPreset',
        description = '2nd Generation Data Acquisition',
        daqpvprefix = countprefix,
        channels = ['protoncount'],
        time_channel = ['elapsedtime'],
    ),
    ThresholdChannel = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThresholdChannel',
        description = "Value of this channel is compared against the Threshold device",
        daqpvprefix = countprefix,
        channels = ['protoncount'],
    ),
    Threshold = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThreshold',
        description = "If the value of ThresholdChannel is below the value of this device, the counterbox is paused",
        daqpvprefix = countprefix,
        min_rate_channel = 'ThresholdChannel',
    ),
    Gate1 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQGate',
        description = "Gate 1 of the counter box",
        daqpvprefix = countprefix,
        channel = 1,
    ),
    Gate2 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQGate',
        description = "Gate 2 of the counter box",
        daqpvprefix = countprefix,
        channel = 2,
    ),
    protoncount = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor for proton current',
        daqpvprefix = countprefix,
        channel = 5,
        type = 'monitor',
    ),
    histogrammer = device('nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description = "Histogram Memory Channel",
        connector = 'hm_connector'
    ),
    camea_detector = device('nicos_sinq.devices.sinqhm.channel.ReshapeHistogramImageChannel',
        description = "Image channel for area detector",
        visibility = (),
        bank = 'hm_bank0',
        dimensions = {
            'x': 1024,
            'y': 104
        },
        connector = 'hm_connector',
    ),
    counts = device('nicos.devices.generic.detector.RectROIChannel',
        description = 'Counts as ROI on camea detector',
        roi = (1, 2, 50, 60)
    ),
    cameadet = device(
        'nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'Detector Interface',
        timers = ['elapsedtime'],
        monitors = ['DAQPreset', 'protoncount'],
        images = ['camea_detector'],
        counters = [
            'counts',
        ],
        postprocess = [
            ('counts', 'camea_detector'),
        ],
        others = ['histogrammer'],
        liveinterval = 20,
        saveintervals = [900]
    ),
)

for i in range(4):
    devices[f'monitor{i+1}'] = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = f'Monitor {i + 1}',
        daqpvprefix = countprefix,
        channel = i + 1,
        type = 'monitor',
    )
    devices['DAQPreset'][1]['channels'].append(f'monitor{i+1}')
    devices['ThresholdChannel'][1]['channels'].append(f'monitor{i+1}')
    devices['cameadet'][1]['monitors'].append(f'monitor{i+1}')

startupcode = """
SetDetectors(cameadet)
DAQPreset.monitor_channel = 'monitor2'
move(ThresholdChannel, 'monitor2')
move(Threshold, 200)
"""
