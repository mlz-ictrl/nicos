description = 'HM configuration for the FOCUS 2D detector'

includes = [
    'focus2d_config',
]

devices = dict(
    mdif_f2d = device('nicos.devices.epics.EpicsAnalogMoveable',
        description = '2D Detector MDIF',
        readpv = "SQ:FOCUS:mdif2d:DELAY_RBV",
        writepv = "SQ:FOCUS:mdif2d:DELAY",
        fmtstr = '%.1f',
        monitor = True,
    ),
    f2d_histogrammer = device('nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description = "2D detector Channel",
        connector = 'f2d_connector'
    ),
    f2d_image = device('nicos_sinq.devices.sinqhm.channel'
        '.HistogramImageChannel',
        description = "Image channel for 2D detector",
        bank = 'f2d_bank',
        connector = 'f2d_connector',
    ),
    f2d_detector = device('nicos.devices.generic.detector.Detector',
        description = '2D detector',
        others = [
            'f2d_histogrammer',
        ],
        images = [
            'f2d_image',
        ],
        visibility = ()
    ),
)
startupcode = """
focusdet.find_followers()
"""
