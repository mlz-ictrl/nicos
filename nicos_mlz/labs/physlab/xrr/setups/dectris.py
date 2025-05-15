description = 'detector'
group = 'optional'

tango_base = configdata('instrument.values')['tango_base']

sysconfig = dict(
    datasinks = [
        # 'tiffformat',
        'rawfile',
        'caresssink'
        # 'textsink',
    ],
)

devices = dict(
    timer = device('nicos.devices.entangle.TimerChannel',
        description = 'timer for detector',
        tangodevice = tango_base + 'box/dectris/timer',
    ),
    image = device('nicos_mlz.labs.physlab.devices.dectris.Detector',
        description = 'image for detector',
        tangodevice = tango_base + 'box/dectris/image',
        pixel_size = (64 / 1280, 8), # mm
        pixel_count = 1280,
        config = device('nicos_jcns.devices.dectris.ConfigurationChannel',
            description = 'Configuration channel of the DECTRIS MYTHEN R 1K detector.',
            tangodevice = tango_base + 'box/dectris/config',
        ),
        flip = True,
    ),
    ysd = device('nicos.devices.generic.ManualMove',
        description = 'Distance sample to detector',
        fmtstr = '%.1f',
        default = 305,
        unit = 'mm',
        abslimits = (50, 400),
        requires = {'level': 'admin'},
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Merge detector infos',
        timers = ['timer'],
        images = ['image'],
        counters = ['roi1', 'roi2'],
        postprocess = [
            ('roi1', 'image'),
            ('roi2', 'image'),
        ],
    ),
    roi1 = device('nicos.devices.generic.RectROIChannel',
        description = 'ROI 1',
        roi = (0, 0, 1280, 1),
    ),
    roi2 = device('nicos.devices.generic.RectROIChannel',
        description = 'ROI 2',
        roi = (0, 0, 1280, 1),
    ),
    rawfile = device('nicos.devices.datasinks.raw.SingleRawImageSink',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.raw']
    ),
    textsink = device('nicos.devices.datasinks.text.NPFileSink',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.dat']
    ),
    caresssink = device('nicos_mlz.stressi.datasinks.CaressScanfileSink',
        filenametemplate = ['xresd%(scancounter)08d.dat'],
        detectors = ['det'],
    ),
)

startupcode = '''
SetDetectors(det)
'''
