# -*- coding: utf-8 -*-

description = "Detector data acquisition setup"
group = "lowlevel"
display_order = 25

includes = ['counter']
excludes = ['virtual_daq']

sysconfig = dict(
    datasinks = ['kwsformat', 'yamlformat'],
)

tango_base = "tango://phys.kws2.frm2:10000/kws2/"

devices = dict(
    det_img    = device('kws1.daq.KWSImageChannel',
                        description = 'Image for the large KWS detector',
                        tangodevice = tango_base + 'gedet/image',
                        timer = 'timer',
                        fmtstr = '%d (%.1f cps)',
                       ),

    det_mode   = device('devices.generic.ReadonlyParamDevice',
                        description = 'Current detector mode',
                        device = 'det_img',
                        parameter = 'mode',
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
                        monitors = ['mon1', 'mon2', 'selctr'],
                        images = ['det_img'],
                        others = [],
                        shutter = 'shutter',
                        liveinterval = 2.0,
                       ),
)

extended = dict(
    poller_cache_reader = ['shutter'],
)
