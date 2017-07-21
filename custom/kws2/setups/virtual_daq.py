# -*- coding: utf-8 -*-

description = "Detector data acquisition setup"
group = "lowlevel"
display_order = 25

sysconfig = dict(
    datasinks = ['kwsformat', 'yamlformat'],
)

includes = ['virtual_gedet']

devices = dict(
    kwsformat  = device('nicos_mlz.kws2.devices.kwsfileformat.KWSFileSink',
                        lowlevel = True,
                        transpose = True,
                        detectors = ['det'],
                       ),

    yamlformat = device('nicos_mlz.kws2.devices.yamlformat.YAMLFileSink',
                        lowlevel = True,
                        detectors = ['det'],
                       ),

    det_mode   = device('nicos.devices.generic.ReadonlyParamDevice',
                        description = 'Current detector mode',
                        device = 'det_img',
                        parameter = 'mode',
                       ),

    det_img_ge = device('nicos_mlz.kws1.devices.daq.VirtualKWSImageChannel',
                        description = 'Image for the large KWS detector',
                        sizes = (144, 256),
                       ),

    det_img_jum = device('nicos_mlz.kws1.devices.daq.VirtualKWSImageChannel',
                        description = 'Image for the small KWS detector',
                        sizes = (256, 256),
                       ),

    det        = device('nicos_mlz.kws1.devices.daq.KWSDetector',
                        description = 'KWS detector',
                        timers = ['timer'],
                        monitors = ['mon1', 'mon2'],
                        images = ['det_img'],
                        others = [],
                        shutter = 'shutter',
                        liveinterval = 2.0,
                       ),

    det_img    = device('nicos.devices.generic.DeviceAlias',
                        alias = 'det_img_ge',
                        devclass = 'kws1.daq.VirtualKWSImageChannel',
                       ),

    timer      = device('nicos.devices.generic.VirtualTimer',
                        description = 'Measurement timer channel',
                        fmtstr = '%.0f',
                       ),

    mon1       = device('nicos.devices.generic.VirtualCounter',
                        description = 'Monitor 1 (before selector)',
                        type = 'monitor',
                        fmtstr = '%d',
                        lowlevel = True,
                       ),

    mon2       = device('nicos.devices.generic.VirtualCounter',
                        description = 'Monitor 2 (after selector)',
                        type = 'monitor',
                        fmtstr = '%d',
                        lowlevel = True,
                       ),
)

extended = dict(
    poller_cache_reader = ['shutter'],
)
