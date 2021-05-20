description = 'HM configuration for the FOCUS upper detector bank'

includes = [
    'upperbank_config',
]

group = 'lowlevel'

devices = dict(
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
        lowlevel = True
    ),
)
startupcode = """
focusdet.find_slaves()
"""
