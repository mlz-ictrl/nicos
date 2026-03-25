description = 'HM configuration for the FOCUS lower detector bank'

group = 'lowlevel'

includes = [
    'lowerbank_config',
]

devices = dict(
    mdif_lower = device('nicos.devices.epics.EpicsAnalogMoveable',
        description = 'Lower Detector MDIF',
        readpv = "SQ:FOCUS:mdiflower:DELAY_RBV",
        writepv = "SQ:FOCUS:mdiflower:DELAY",
        fmtstr = '%.1f',
        monitor = True,
    ),
    lower_histogrammer = device('nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description = "Lower bank HM Channel",
        connector = 'lower_connector'
    ),
    lower_image = device('nicos_sinq.devices.sinqhm.channel.HistogramImageChannel',
        description = "Image channel lower bank",
        bank = 'hm_lower',
        connector = 'lower_connector',
    ),
    lower_detector = device('nicos.devices.generic.detector.Detector',
        description = 'Lower bank detector',
        others = [
            'lower_histogrammer',
        ],
        images = [
            'lower_image',
        ],
        visibility = ()
    ),
)
startupcode = """
focusdet.find_followers()
"""
