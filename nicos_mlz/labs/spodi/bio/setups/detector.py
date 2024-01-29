description = 'Keyence readout'

group = 'lowlevel'

devices = dict(
    keyence = device('nicos_mlz.labs.spodi.bio.devices.keyence.KeyenceImage',
        rotation = 90,
        visibility = {'metadata', 'namespace'},
    ),
    tim1 = device('nicos.devices.generic.VirtualTimer',
        visibility = {'metadata', 'namespace'},
    ),
    roi = device('nicos.devices.generic.RectROIChannel',
        description = 'ROI',
        # roi = (750, 500, 500, 1000),
        roi = (500, 750, 1000, 500),
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Detector',
        images = ['keyence'],
        timers = ['tim1'],
        counters = ['roi'],
        postprocess = [
            ('roi', 'keyence'),
        ],
    ),
)

startupcode = '''
SetDetectors(det)
'''
