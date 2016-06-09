# -*- coding: utf-8 -*-

description = "Detector data acquisition setup"
group = "lowlevel"

sysconfig = dict(
    datasinks = ['kwsformat', 'yamlformat'],
)

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

    mon2       = device('devices.generic.virtual.VirtualCounter',
                        description = 'monitor',
                        type = 'monitor',
                       ),

    mon3       = device('devices.generic.virtual.VirtualCounter',
                        description = 'monitor',
                        type = 'monitor',
                       ),

    kwsformat  = device('kws1.kwsfileformat.KWSFileSink',
                        lowlevel = True,
                       ),

    yamlformat = device('kws1.yamlformat.YAMLFileSink',
                        lowlevel = True,
                       ),

    det        = device('kws1.daq.KWSDetector',
                        description = 'KWS detector',
                        timers = ['timer'],
                        monitors = ['mon1', 'mon2', 'mon3'],
                        images = ['det_img'],
                        others = [],
                        shutter = 'shutter',
                       ),
)

extended = dict(
    poller_cache_reader = ['shutter'],
)
