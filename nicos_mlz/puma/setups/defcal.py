description = 'Calibration of the deflectors'

group = 'basic'

includes = [
    'pumabase', 'seccoll', 'collimation', 'ios', 'hv', 'notifiers', 'multidet',
    'multiana', 'rdcad', 'opticalbench', 'detector', 'ana_alias', 'pollengths',
    'slits',
]

sysconfig = dict(
    datasinks = ['polsink',]
)

nethost = 'pumasrv.puma.frm2'

devices = dict(
    peak1 = device("nicos.devices.generic.RectROIChannel",
        description = "Peak 1",
        roi = (250, 0, 120, 7),
    ),
    peak2 = device("nicos.devices.generic.RectROIChannel",
        description = "Peak 2",
        roi = (370, 0, 150, 7),
    ),
    peak3 = device("nicos.devices.generic.RectROIChannel",
        description = "Peak 3",
        roi = (520, 0, 160, 7),
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Puma detector QMesydaq device (PSD setup)',
        timers = ['timer'],
        monitors = ['mon1'],
        images = ['image'],
        counters = ['peak1', 'peak2', 'peak3'],
        maxage = 86400,
        pollinterval = None,
        postprocess = [
            ('peak1', 'image'),
            ('peak2', 'image'),
            ('peak3', 'image'),
        ],
    ),
    polsink = device('nicos_mlz.puma.devices.datasinks.PolarizationFileSink',
        description = 'writes the files for polarisation analysis',
    ),
)

startupcode = '''
SetDetectors(det)
set('image', 'listmode', False)
'''
