# -*- coding: utf-8 -*-

description = "Detector data acquisition setup"
group = "lowlevel"
display_order = 25

sysconfig = dict(
    datasinks = ['kwsformat', 'yamlformat'],
)

includes = ['virtual_gedet']

devices = dict(
    kwsformat  = device('kws1.kwsfileformat.KWSFileSink',
                        lowlevel = True,
                       ),

    yamlformat = device('kws1.yamlformat.YAMLFileSink',
                        lowlevel = True,
                       ),

    det_mode   = device('devices.generic.ReadonlyParamDevice',
                        description = 'Current detector mode',
                        device = 'det_img',
                        parameter = 'mode',
                       ),

    det_img_ge = device('kws1.daq.VirtualKWSImageChannel',
                        description = 'Image for the large KWS detector',
                        resolution = (144, 256),
                       ),

    det_img_jum = device('kws1.daq.VirtualKWSImageChannel',
                        description = 'Image for the small KWS detector',
                        resolution = (256, 256),
                       ),

    det        = device('kws1.daq.KWSDetector',
                        description = 'KWS detector',
                        timers = ['timer'],
                        monitors = ['mon1', 'mon2'],
                        images = ['det_img'],
                        others = [],
                        shutter = 'shutter',
                        liveinterval = 2.0,
                       ),

    det_img    = device('devices.generic.DeviceAlias',
                        alias = 'det_img_ge',
                        devclass = 'kws1.daq.VirtualKWSImageChannel',
                       ),

    timer      = device('devices.generic.virtual.VirtualTimer',
                        description = 'Measurement timer channel',
                        fmtstr = '%.0f',
                       ),

    mon1       = device('devices.generic.virtual.VirtualCounter',
                        description = 'Monitor 1 (before selector)',
                        type = 'monitor',
                        fmtstr = '%d',
                        lowlevel = True,
                       ),

    mon2       = device('devices.generic.virtual.VirtualCounter',
                        description = 'Monitor 2 (after selector)',
                        type = 'monitor',
                        fmtstr = '%d',
                        lowlevel = True,
                       ),
)

extended = dict(
    poller_cache_reader = ['shutter'],
)
