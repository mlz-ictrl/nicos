description = 'Setup for the CAMEA detector'

includes = [
    'hm_config',
]  # The real thing
#includes=['hm_config_sim',] # For simulation

pvprefix = 'SQ:CAMEA:counter'

devices = dict(
    timepreset = device('nicos_ess.devices.epics.detector.EpicsTimerActiveChannel',
        epicstimeout = 3.0,
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = pvprefix + '.TP',
        presetpv = pvprefix + '.TP',
    ),
    elapsedtime = device('nicos_ess.devices.epics.detector.EpicsTimerPassiveChannel',
        epicstimeout = 3.0,
        description = 'Used to view elapsed time while counting',
        unit = 'sec',
        readpv = pvprefix + '.T',
    ),
    monitorpreset = device('nicos_ess.devices.epics.detector.EpicsCounterActiveChannel',
        epicstimeout = 3.0,
        description = 'Used to set and view monitor preset',
        type = 'monitor',
        readpv = pvprefix + '.PR2',
        presetpv = pvprefix + '.PR2',
    ),
    monitor1 = device('nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout = 3.0,
        description = 'First scalar counter channel',
        type = 'monitor',
        readpv = pvprefix + '.S2',
    ),
    monitor2 = device('nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout = 3.0,
        description = 'Second scalar counter channel',
        type = 'monitor',
        readpv = pvprefix + '.S3',
    ),
    monitor3 = device('nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout = 3.0,
        description = 'Third scalar counter channel',
        type = 'monitor',
        lowlevel = False,
        readpv = pvprefix + '.S4',
    ),
    monitor4 = device('nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout = 3.0,
        description = 'Fourth scalar counter channel',
        type = 'monitor',
        lowlevel = False,
        readpv = pvprefix + '.S5',
    ),
    protoncount = device('nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        epicstimeout = 3.0,
        description = 'Fourth scalar counter channel',
        type = 'monitor',
        readpv = pvprefix + '.S5',
    ),
    histogrammer = device('nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description = "Histogram Memory Channel",
        connector = 'hm_connector'
    ),
    camea_detector = device('nicos_sinq.devices.sinqhm.channel.ReshapeHistogramImageChannel',
        description = "Image channel for area detector",
        lowlevel = True,
        bank = 'hm_bank0',
        dimensions = {
            'x': 104,
            'y': 1024
        },
        connector = 'hm_connector',
    ),
    counts = device('nicos.devices.generic.detector.RectROIChannel',
        description = 'Counts as ROI on camea detector',
        roi = (1, 2, 50, 60)
    ),
    cameadet = device('nicos_sinq.devices.detector.SinqDetector',
        epicstimeout = 3.0,
        description = 'EL737 counter box that counts neutrons and '
        'starts streaming events',
        startpv = pvprefix + '.CNT',
        pausepv = pvprefix + ':Pause',
        statuspv = pvprefix + ':Status',
        errormsgpv = pvprefix + ':MsgTxt',
        thresholdpv = pvprefix + ':Threshold',
        thresholdcounterpv = pvprefix + ':ThresholdCounter',
        monitorpreset = 'monitorpreset',
        timepreset = 'timepreset',
        timers = ['elapsedtime'],
        monitors = [
            'monitor1', 'monitor2', 'monitor3', 'protoncount', 'monitor4'
        ],
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
    )
)
startupcode = """
SetDetectors(cameadet)
"""
