description = 'HM configuration for the FOCUS lower detector bank'

includes = [
    'lowerbank_config',
]

group = 'lowlevel'

devices = dict(
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
        lowlevel = True
    ),
)
startupcode = """
focusdet.find_slaves()
"""
