# -*- coding: utf-8 -*-

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
    image = device('nicos.devices.entangle.ImageChannel',
        description = 'image for detector',
        tangodevice = tango_base + 'box/dectris/image',
    ),
    ysd = device('nicos.devices.generic.ManualMove',
        description = 'Distance sample to detector',
        fmtstr = '%.1f',
        default = 201.984,
        unit = 'mm',
        abslimits = (50, 400),
        requires = {'level': 'admin'},
    ),
    ttheta = device('nicos_mlz.labs.physlab.xresd.devices.ttheta.Detector',
        description = 'Detector ...',
        det = 'image',
        # ttheta = 'stt',
        # radius = 201.984, # mm
        pixel_size = 50/1000.0, # mm
        pixel_count = 1280,
    ),
    adet = device('nicos.devices.generic.Detector',
        description = 'Merge detector infos',
        timers = ['timer'],
        images = ['ttheta'],
    ),
    det = device('nicos.devices.generic.DeviceAlias',
        alias = 'adet',
        visibility = {'metadata', 'namespace'},
    ),
    sdet = device('nicos_mlz.labs.physlab.xresd.devices.detector.MovingDetector',
        description = 'Moving detector ... ',
        motor = 'ctt',
        detector = 'det',
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
