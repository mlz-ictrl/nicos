description = 'HM configuration for the FOCUS upper detector bank'

group = 'lowlevel'

includes = [
    'upperbank_config',
]

devices = dict(
    mdif_upper = device('nicos.devices.epics.EpicsAnalogMoveable',
        description = 'Upper Detector MDIF',
        readpv = "SQ:FOCUS:mdifupper:DELAY_RBV",
        writepv = "SQ:FOCUS:mdifupper:DELAY",
        fmtstr = '%.1f',
        monitor = True,
    ),
    upper_histogrammer = device('nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description = "Upper bank HM Channel",
        connector = 'upper_connector'
    ),
    upper_image = device('nicos_sinq.devices.sinqhm.channel.HistogramImageChannel',
        description = "Image channel upper bank",
        bank = 'hm_upper',
        connector = 'upper_connector',
    ),
    upper_detector = device('nicos.devices.generic.detector.Detector',
        description = 'Upper bank detector',
        others = [
            'upper_histogrammer',
        ],
        images = [
            'upper_image',
        ],
        visibility = ()
    ),
)
startupcode = """
focusdet.find_followers()
"""
