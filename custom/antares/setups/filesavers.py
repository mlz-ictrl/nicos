# -*- coding: utf-8 -*-

description = 'Detector file savers'

group = 'lowlevel'

sysconfig = dict(
    datasinks = ['conssink', 'filesink', 'daemonsink', 'FITSFileSaver'],
)

devices = dict(
    FITSFileSaver = device('devices.datasinks.FITSImageSink',
                           description = 'Saves image data in FITS format',
                           filenametemplate = ['%(pointcounter)08d.fits'],
                          ),
)
