description = 'HM configuration for the FOCUS middle  detector bank'

group = 'lowlevel'

includes = [
    'middlebank_config',
]

devices = dict(
    mdif_middle = device('nicos.devices.epics.EpicsAnalogMoveable',
        description = 'Middle Detector MDIF',
        readpv = "SQ:FOCUS:mdifmiddle:DELAY_RBV",
        writepv = "SQ:FOCUS:mdifmiddle:DELAY",
        fmtstr = '%.1f',
        monitor = True,
    ),
    middle_histogrammer = device('nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description = "Middle bank HM Channel",
        connector = 'middle_connector'
    ),
    middle_image = device('nicos_sinq.devices.sinqhm.channel.HistogramImageChannel',
        description = "Image channel Middle bank",
        bank = 'hm_middle',
        connector = 'middle_connector',
    ),
    middle_detector = device('nicos.devices.generic.detector.Detector',
        description = 'Middle bank detector',
        others = [
            'middle_histogrammer',
        ],
        images = [
            'middle_image',
        ],
        visibility = ()
    ),
)
startupcode = """
focusdet.find_followers()
"""
