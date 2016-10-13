# -*- coding: utf-8 -*-

description = 'Detector file savers'

group = 'lowlevel'

sysconfig = dict(
    datasinks = ['FITSFileSaver', 'DiObSink'],
)

devices = dict(
    FITSFileSaver = device('devices.datasinks.FITSImageSink',
                           description = 'Saves image data in FITS format',
                           filenametemplate = ['%(pointcounter)08d.fits'],
                          ),
    DiObSink = device('frm2.datasinks.DiObSink',
                      description = 'Updates di/ob links',
                     ),
)
