# -*- coding: utf-8 -*-

description = 'Take images from webcam before every image'
group = 'optional'
display_order = 10

sysconfig = dict(
    datasinks = ['webcam_sink'],
)

devices = dict(
    webcam_sink = device('nicos_mlz.kws3.devices.webcam.WebcamSink',
        description = 'Takes webcam image for every count',
        url = 'http://kws3:kws3@cam3.kws3.frm2/jpg/1/image.jpg',
        filenametemplate = ['pre_%(pointcounter)08d.jpg'],
        lowlevel = False,  # explicitly
    ),
)
