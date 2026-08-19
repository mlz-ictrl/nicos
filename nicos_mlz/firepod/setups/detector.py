description = 'FirePOD detector'

group = 'lowlevel'

includes = [
    'hv1', 'hv2', 'hv3', 'hv4', 'hv5', 'hv6', 'hv7', 'hv8',
]

devices = dict(
    hv = device('nicos_mlz.firepod.devices.detectorhv.DetectorHV',
        description = 'Detector HV switch',
        channels = [
            'det1_hv',
            'det2_hv',
            'det3_hv',
            'det4_hv',
            'det5_hv',
            'det6_hv',
            'det7_hv',
            'det8_hv',
        ],
    ),
)
