description = 'EMBL Detector and Histogram Memory'

group = 'basic'

includes = [
    'el737',
    'embl_config',
]

sysconfig = dict(datasinks = ['hmlivesink'])

devices = dict(
    # Histogrammer Specific
    histogrammer = device('nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description = "Histogram Memory Channel",
        connector = 'hm_connector'
    ),
    area_detector = device('nicos_sinq.devices.sinqhm.channel.HistogramImageChannel',
        description = "Image channel for area detector",
        bank = 'hm_bank0',
        connector = 'hm_connector',
    ),

    # Other
    chopper_delay = device('nicos.devices.epics.pva.epics_devices.EpicsAnalogMoveable',
        description = 'EMBL MDIF Unit',
        readpv = "SQ:BOA:MDIF:DELAY_RBV",
        writepv = "SQ:BOA:MDIF:DELAY",
        fmtstr = '%.1f',
        monitor = True,
    ),
    hmlivesink = device('nicos_sinq.boa.devices.sinks.HMLiveViewSink',
        description = "Sink for forwarding histogrammer live data to the GUI",
    ),
    chopper_embl_distance = device('nicos.devices.generic.manual.ManualMove',
        description = "Distance from Chopper to EMBL Detector",
        abslimits = (0, 20),
        unit = 'm',
    ),

    # Detector Device
    embl_tof = device('nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'Detector Nicos Device',
        timers = ['elapsedtime'],
        monitors = ['hardware_preset', 'monitorval', 'protoncurr'],
        images = ['area_detector'],
        others = ['histogrammer'],
        liveinterval = 20,
        saveintervals = [60],
        visibility = {'metadata', 'namespace'},
    ),
)

startupcode = '''
SetDetectors(embl_tof)
'''
