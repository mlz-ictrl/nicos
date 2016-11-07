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

    det_img_ge = device('kws2.daq.GEImageChannel',
                        description = 'Image for the large KWS detector',
                        tangodevice = tango_base + 'ge/det',
                        timer = 'timer',
                        highvoltage = 'gedet_HV',
                        fmtstr = '%d (%.1f cps)',
                       ),

    det_img_jum = device('kws1.daq.KWSImageChannel',
                        description = 'Image for the small KWS detector',
                        tangodevice = tango_base + 'jumiom/det',
                        timer = 'timer',
                        fmtstr = '%d (%.1f cps)',
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

    det_img    = device('devices.generic.DeviceAlias',
                        alias = 'det_img_ge',
                        devclass = 'kws1.daq.KWSImageChannel',
                       ),
)

extended = dict(
    poller_cache_reader = ['shutter', 'gedet_HV'],
)
