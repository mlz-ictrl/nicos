description = 'HM configuration for the FOCUS middle  detector bank'

includes = [
    'middlebank_config',
]

group = 'lowlevel'

devices = dict(
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
        lowlevel = True
    ),
)
startupcode = """
focusdet.find_slaves()
"""
