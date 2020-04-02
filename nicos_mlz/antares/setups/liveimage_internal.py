# -*- coding: utf-8 -*-

description = 'File saver for live image'

group = 'optional'

sysconfig = dict(
    datasinks = ['InternalLivePNGSink'],
)

devices = dict(
    InternalLivePNGSink = device('nicos.devices.datasinks.PNGLiveFileSink',
        description = 'Saves live image as .png every now and then',
        filename = '/antarescontrol/liveimage_internal/live_lin.png',
        log10 = False,
        interval = 15,
        rgb = False,
        size = 512,
        histrange = (0.02, 0.98),
    ),
)
