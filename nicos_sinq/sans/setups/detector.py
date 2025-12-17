description = 'Devices for the Detector'

group = 'basic'

includes = ['attenuator', 'velocity_selector', 'beamstop', 'collimator_s7', 
        'sample', 'shutter', 'asyncontroller', 'detector_motors', 'hm_config']
excludes = ['detector_old', 'detector_strobo']

# TODO/WARNING removed includes hm_config, as it conflict with strobo, partition and create a basic meta group for detector without strobo 

pvprefix = 'SQ:SANS:motb:'
pvdprefix = 'SANSCNTBOX1'

sysconfig = dict(
    datasinks = ['LivePNGSink', 'LivePNGSinkLog']
)

devices = dict(
    LivePNGSinkLog = device('nicos.devices.datasinks.PNGLiveFileSink',
        description = 'Saves live image as .png every now and then',
        filename = '/home/sans/data/html/live_log.png',
        log10 = True,
        interval = 15,
        detectors = ['sansdet']
    ),
    LivePNGSink = device('nicos.devices.datasinks.PNGLiveFileSink',
        description = 'Saves live image as .png every now and then',
        filename = '/home/sans/data/html/live_lin.png',
        log10 = False,
        interval = 15,
        detectors = ['sansdet'],
    ),
    elapsedtime = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQTime',
        daqpvprefix = pvdprefix,
    ),
    DAQPreset = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQPreset',
        description = '2nd Generation Data Acquisition',
        daqpvprefix = pvdprefix,
        channels = ['protoncount'],
        time_channel = ['elapsedtime'],
    ),
    ThresholdChannel = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThresholdChannel',
        daqpvprefix = pvdprefix,
        channels = ['protoncount'],
    ),
    Threshold = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThreshold',
        daqpvprefix = pvdprefix,
        min_rate_channel = 'ThresholdChannel',
    ),
    protoncount = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor for proton current',
        daqpvprefix = pvdprefix,
        channel = 5,
        type = 'monitor',
    ),
    histogrammer = device('nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description = "Histogram Memory Channel",
        connector = 'hm_connector'
    ),
    sans_detector = device('nicos_sinq.devices.sinqhm.channel.ReshapeHistogramImageChannel',
        description = "Image channel for area detector",
        visibility = (),
        bank = 'hm_bank0',
        connector = 'hm_connector',
        dimensions = {
            'x': 128,
            'y': 128
        },
    ),
    sansdet = device(
        'nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'EL737 counter box that counts neutrons and starts streaming events',
        timers = ['elapsedtime'],
        monitors = ['DAQPreset', 'protoncount'],
        images = ['sans_detector'],
        counters = [],
        others = ['histogrammer'],
        liveinterval = 7,
        saveintervals = [60]
    ),
)

for i in range(8):
    devices[f'monitor{i+1}'] = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = f'Monitor {i + 1}',
        daqpvprefix = pvdprefix,
        channel = i + 1,
        type = 'monitor',
    )
    devices['DAQPreset'][1]['channels'].append(f'monitor{i+1}')
    devices['ThresholdChannel'][1]['channels'].append(f'monitor{i+1}')
    devices['sansdet'][1]['monitors'].append(f'monitor{i+1}')

startupcode = """
hm_configurator.updateConfig()
SetDetectors(sansdet)
"""
