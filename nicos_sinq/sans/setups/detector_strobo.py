description = 'Devices for the Detector'

group = 'basic'

includes = ['hm_config_strobo', 'attenuator', 'velocity_selector', 'beamstop', 'collimator_s7', 
            'sample', 'shutter', 'asyncontroller', 'detector_motors']
excludes = ['detector']

pvdprefix = 'SANSCNTBOX1'

channels = ['monitor1', 'monitor2', 'monitor3', 'monitor4', 'monitor5', 'protoncount', 'monitor6', 'monitor7',  'monitor8']


devices = dict(
    elapsedtime = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQTime',
        daqpvprefix = pvdprefix,
    ),
    DAQPreset = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQPreset',
        description = '2nd Generation Data Acquisition',
        daqpvprefix = pvdprefix,
        channels = channels,
        time_channel = ['elapsedtime'],
    ),
    ThresholdChannel = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThresholdChannel',
        daqpvprefix = pvdprefix,
        channels = channels,
    ),
    Threshold = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThreshold',
        daqpvprefix = pvdprefix,
        min_rate_channel = 'ThresholdChannel',
    ),
    monitor1 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor 1',
        daqpvprefix = pvdprefix,
        channel = 1,
        type = 'monitor',
    ),
    monitor2 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor 2',
        daqpvprefix = pvdprefix,
        channel = 2,
        type = 'monitor',
    ),
    monitor3 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor 3',
        daqpvprefix = pvdprefix,
        channel = 3,
        type = 'monitor',
        visibility = {'metadata', 'namespace', 'devlist'},
    ),
    monitor4 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor 4',
        daqpvprefix = pvdprefix,
        channel = 4,
        type = 'monitor',
        visibility = {'metadata', 'namespace', 'devlist'},
    ),
    monitor5 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor 4',
        daqpvprefix = pvdprefix,
        channel = 5,
        type = 'monitor',
        visibility = {'metadata', 'namespace', 'devlist'},
    ),
    protoncount = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor for proton current',
        daqpvprefix = pvdprefix,
        channel = 5,
        type = 'monitor',
    ),
    monitor6 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor before sample',
        daqpvprefix = pvdprefix,
        channel = 6,
        type = 'monitor',
    ),
    monitor7 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor after chopper',
        daqpvprefix = pvdprefix,
        channel = 7,
        type = 'monitor',
    ),
    monitor8 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor before chopper',
        daqpvprefix = pvdprefix,
        channel = 8,
        type = 'monitor',
        visibility = {'metadata', 'namespace', 'devlist'},
    ),
    histogrammer = device('nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description = "Histogram Memory Channel",
        connector = 'hm_connector'
    ),
    sans_detector = device('nicos_sinq.sans.devices.sanschannel.StroboHistogramImageChannel',
        description = "Image channel for area detector",
        visibility = ('metadata', 'namespace', 'devlist'),
        bank = 'hm_bank0',
        dimensions = {
            'x': 128,
            'y': 128
        },
        connector = 'hm_connector',
        tof_axis = 'hm_ax_tof',
    ),
    sans_raw_hmbank = device('nicos_sinq.devices.sinqhm.channel.HistogramImageChannel',
        description = "Image channel for area detector",
        visibility = ('metadata', 'namespace', 'devlist'),
        bank = 'hm_bank0',
        connector = 'hm_connector',
    ),
    sans_slice = device('nicos_sinq.devices.channel.SelectSliceImageChannel',
        description = 'Slice selector',
        data_channel = 'sans_detector'
    ),
    sansdet = device(
        'nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'EL737 counter box that counts neutrons and starts streaming events',
        timers = ['elapsedtime'],
        monitors = ['DAQPreset'] + channels,
        images = ['sans_detector', 'sans_raw_hmbank'],
        counters = [],
        others = ['histogrammer', 'sans_slice'],
        liveinterval = 7,
        saveintervals = [60]
    ),
)
startupcode = """
hm_configurator.updateConfig()
SetDetectors(sansdet)
"""
