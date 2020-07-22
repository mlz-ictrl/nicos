# -*- coding: utf-8 -*-

description = 'Detector file savers'

group = 'lowlevel'

sysconfig = dict(
    datasinks = ['FITSFileSaver'],  # , 'DiObSink'],
)

devices = dict(
    FITSFileSaver = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['%(pointcounter)08d.fits'],
        filemode = 0o444,
    ),
    DiObSink = device('nicos_mlz.devices.datasinks.DiObSink'),
)
