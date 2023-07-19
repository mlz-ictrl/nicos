description = 'detector'
group = 'optional'

tango_base = configdata('instrument.values')['tango_base']

sysconfig = dict(
    datasinks = [
        # 'tiffformat',
        # 'fileformat',
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
        pixel_size = 50 / 1000.0, # mm
        pixel_count = 1280,
    ),
    ysd = device('nicos.devices.generic.ManualMove',
        description = 'Distance sample to detector',
        fmtstr = '%.1f',
        default = 201.984,
        unit = 'mm',
        abslimits = (50, 400),
        requires = {'level': 'admin'},
    ),
    adet = device('nicos.devices.generic.Detector',
        description = 'Merge detector infos',
        timers = ['timer'],
        images = ['image'],
    ),
    # det = device('nicos.devices.generic.DeviceAlias',
    #     alias = 'adet',
    #     visibility = {'metadata', 'namespace'},
    # ),
    sdet = device('nicos_mlz.labs.physlab.devices.detector.MovingDetector',
        description = 'Moving detector ... ',
        motor = 'ctt',
        detector = 'adet',
    ),
    fileformat = device('nicos.devices.datasinks.raw.SingleRawImageSink',
        # filenametemplate = ['%(proposal)s_%(pointcounter)08d.txt']
    ),
    textsink = device('nicos.devices.datasinks.text.NPFileSink',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.dat']
    ),
    caresssink = device('nicos_mlz.stressi.datasinks.CaressScanfileSink',
        filenametemplate = ['xresd%(scancounter)08d.dat'],
        detectors = ['adet'],
        # flipimage = True,
    ),
)

startupcode = '''
SetDetectors(adet)
'''
