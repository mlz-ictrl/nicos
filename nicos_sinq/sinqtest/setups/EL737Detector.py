description = 'Devices for the detectors'

countprefix = 'SQ:SINQTEST:CNTBOX1'

devices = dict(
    Time737 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQTime',
        daqpvprefix = countprefix,
    ),
    Preset737 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQPreset',
        description = '2nd Generation Data Acquisition',
        daqpvprefix = countprefix,
        channels = [],
        time_channel = ['Time737'],
    ),
    DAQ = device(
        'nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'Detector Interface',
        timers = ['Time737'],
        counters = [],
        monitors = ['Preset737'],
        images = [],
        others = [],
        liveinterval = 2,
        saveintervals = [2]
    ),
    ThresholdCh737 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThresholdChannel',
        daqpvprefix = countprefix,
        channels = [],
    ),
    Threshold737 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThreshold',
        daqpvprefix = countprefix,
        min_rate_channel = 'ThresholdCh737',
    ),
)

for i in range(8):
    devices[f'mon{i+1}'] = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = f'Monitor {i + 1}',
        daqpvprefix = countprefix,
        channel = i + 1,
        type = 'monitor',
    )
    devices['Preset737'][1]['channels'].append(f'mon{i+1}')
    devices['ThresholdCh737'][1]['channels'].append(f'mon{i+1}')
    devices['DAQ'][1]['monitors'].append(f'mon{i+1}')

startupcode = '''
SetDetectors(DAQ)
'''
