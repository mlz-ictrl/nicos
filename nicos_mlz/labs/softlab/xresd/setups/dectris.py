# -*- coding: utf-8 -*-

description = 'detector'
group = 'optional'

tango_base = configdata('instrument.values')['tango_base']

sysconfig = dict(
    # datasinks = ['tiffformat'],
    datasinks = ['fileformat'],
    # datasinks = ['textsink'],
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
    ttheta = device('nicos_mlz.labs.softlab.xresd.devices.ttheta.Detector',
        description = 'Detector ...',
        det = 'image',
        ttheta = 'stt',
        radius = 201.984, # mm
        pixel_size = 50/1000.0, # mm
        pixel_count = 1280,
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Merge detector infos',
        timers = ['timer'],
        images = ['ttheta'],
    ),
    sdet = device('nicos_mlz.labs.softlab.xresd.devices.detector.MovingDetector',
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

)
