description = 'BOA Setup File for Redpitaya TOF with counterbox'

group = 'basic'

includes = [
    'redpitaya_tof',
    'el737',
]

devices = dict(
    # RedPitaya TOF Detector
    redpitaya_tof_detector = device('nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'RedPitaya TOF Detector',
        timers = ['elapsedtime'],
        monitors = ['hardware_preset','protoncurr', 'monitorval'],
        images = [
            'ttl_ch0_tof',
            'analog_ch0_tof',
            'analog_ch0_ph',
            'analog_ch1_tof',
            'analog_ch1_ph',
        ],
        others = ['redpitaya_daq_controller'],
        liveinterval = 2,
        saveintervals = [60],
    ),
)

startupcode = '''
SetDetectors(redpitaya_tof_detector)
'''
