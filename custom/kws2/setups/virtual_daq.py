# -*- coding: utf-8 -*-

description = "Detector data acquisition setup"
group = "lowlevel"
display_order = 25

sysconfig = dict(
    datasinks = ['kwsformat', 'yamlformat'],
)

devices = dict(
    det_img    = device('kws1.daq.VirtualKWSImageChannel',
                        description = 'Image for the large KWS detector',
                        resolution = (144, 256),
                       ),

    det_mode   = device('devices.generic.ReadonlyParamDevice',
                        description = 'Current detector mode',
                        device = 'det_img',
                        parameter = 'mode',
                       ),

    timer      = device('devices.generic.virtual.VirtualTimer',
                        description = 'timer',
                        fmtstr = '%.0f',
                       ),

    mon1       = device('devices.generic.virtual.VirtualCounter',
                        description = 'Monitor 1 (before selector)',
                        type = 'monitor',
                        fmtstr = '%d',
                       ),

    mon2       = device('devices.generic.virtual.VirtualCounter',
                        description = 'Monitor 2 (after selector)',
                        type = 'monitor',
                        fmtstr = '%d',
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
                        monitors = ['mon1', 'mon2'],
                        images = ['det_img'],
                        others = [],
                        shutter = 'shutter',
                       ),
)

extended = dict(
    poller_cache_reader = ['shutter'],
)
