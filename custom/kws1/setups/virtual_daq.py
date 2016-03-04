# -*- coding: utf-8 -*-

description = "Detector data acquisition setup"
group = "lowlevel"

devices = dict(
    det_img    = device('kws1.daq.VirtualJDaqChannel',
                        description = 'Image for the large KWS detector',
                       ),

    timer      = device('devices.generic.virtual.VirtualTimer',
                        description = 'timer',
                       ),

    mon1       = device('devices.generic.virtual.VirtualCounter',
                        description = 'monitor',
                        type = 'monitor',
                       ),

    det        = device('kws1.daq.KWSDetector',
                        description = 'KWS detector',
                        timers = ['timer'],
                        monitors = ['mon1'],
                        images = ['det_img'],
                        others = [],
                        fileformats = [],
                        shutter = 'shutter',
                       ),
)
