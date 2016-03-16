# -*- coding: utf-8 -*-

description = 'Detector file savers'

group = 'lowlevel'

devices = dict(
    FITSFileSaver = device('devices.datasinks.FITSImageSink',
                           description = 'Saves image data in FITS format',
                           filenametemplate = ['%08d.fits'],
                          ),
)
