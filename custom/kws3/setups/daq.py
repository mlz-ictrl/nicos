# -*- coding: utf-8 -*-

description = "Detector data acquisition setup"
group = "lowlevel"
display_order = 25

includes = ['counter']
excludes = ['virtual_daq']

sysconfig = dict(
    datasinks = ['kwsformat', 'yamlformat'],
)

tango_base = "tango://phys.kws3.frm2:10000/kws3/"

devices = dict(
    kwsformat  = device('kws1.kwsfileformat.KWSFileSink',
                        lowlevel = True,
                        transpose = True,
                       ),

#    yamlformat = device('kws1.yamlformat.YAMLFileSink',
#                        lowlevel = True,
#                       ),

    det_mode   = device('devices.generic.ReadonlyParamDevice',
                        description = 'Current detector mode',
                        device = 'det_img',
                        parameter = 'mode',
                       ),

    det_img_hrd = device('kws1.daq.KWSImageChannel',
                        description = 'Image for the high-resolution detector',
                        tangodevice = tango_base + 'jumiom/hr_det',
                        timer = 'timer',
                        fmtstr = '%d (%.1f cps)',
                       ),

    det_img_vhrd = device('kws1.daq.KWSImageChannel',
                        description = 'Image for the very high-resolution detector',
                        tangodevice = tango_base + 'jumiom/vhr_det',
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
    poller_cache_reader = ['shutter'],
)
