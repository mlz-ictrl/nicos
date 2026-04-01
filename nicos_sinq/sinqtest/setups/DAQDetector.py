description = 'Devices for the detectors'

countprefix = 'SQ:SINQTEST:CNTBOX2'

devices = dict(
    ElapsedTime = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQTime',
        daqpvprefix = countprefix,
    ),
    DAQPreset = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQPreset',
        description = '2nd Generation Data Acquisition',
        daqpvprefix = countprefix,
        channels = [],
        time_channel = ['ElapsedTime'],
    ),
    DAQV2 = device(
        'nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'Detector Interface',
        timers = ['ElapsedTime'],
        counters = [],
        monitors = ['DAQPreset'],
        images = [],
        others = [],
        liveinterval = 2,
        saveintervals = [2]
    ),
    ThresholdChannel = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThresholdChannel',
        daqpvprefix = countprefix,
        channels = [],
    ),
    Threshold = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThreshold',
        daqpvprefix = countprefix,
        min_rate_channel = 'ThresholdChannel',
    ),
    Gate1 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQGate',
        description = 'Gate channel 1',
        daqpvprefix = countprefix,
        channel = 1,
    ),
    Gate2 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQGate',
        description = 'Gate channel 2',
        daqpvprefix = countprefix,
        channel = 2,
    ),
    TestGen = device('nicos_sinq.devices.epics.sinqdaq.DAQTestGen',
        daqpvprefix = countprefix,
    ),
)

for i in range(10):
    devices[f'monitor{i+1}'] = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = f'Monitor {i + 1}',
        daqpvprefix = countprefix,
        channel = i + 1,
        type = 'monitor',
    )
    devices['DAQPreset'][1]['channels'].append(f'monitor{i+1}')
    devices['ThresholdChannel'][1]['channels'].append(f'monitor{i+1}')
    devices['DAQV2'][1]['monitors'].append(f'monitor{i+1}')

startupcode = '''
SetDetectors(DAQV2)
'''
