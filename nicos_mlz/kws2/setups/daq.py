# -*- coding: utf-8 -*-

description = 'Detector data acquisition setup'
group = 'lowlevel'
display_order = 25

includes = ['counter']
excludes = ['virtual_daq']

sysconfig = dict(
    datasinks = ['kwsformat', 'yamlformat'],
)

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    kwsformat = device('nicos_mlz.kws2.devices.kwsfileformat.KWSFileSink',
        lowlevel = True,
        transpose = True,
        detectors = ['det'],
    ),
    yamlformat = device('nicos_mlz.kws2.devices.yamlformat.YAMLFileSink',
        lowlevel = True,
        detectors = ['det'],
    ),
    det_mode = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Current detector mode',
        device = 'det_img',
        parameter = 'mode',
    ),
    det_img_ge = device('nicos_mlz.kws2.devices.daq.GEImageChannel',
        description = 'Image for the large KWS detector',
        tangodevice = tango_base + 'ge/det',
        timer = 'timer',
        highvoltage = 'gedet_HV',
        fmtstr = '%d (%.1f cps)',
    ),
    det_img_jum = device('nicos_mlz.kws1.devices.daq.KWSImageChannel',
        description = 'Image for the small KWS detector',
        tangodevice = tango_base + 'jumiom/det',
        timer = 'timer',
        fmtstr = '%d (%.1f cps)',
    ),
    det = device('nicos_mlz.kws1.devices.daq.KWSDetector',
        description = 'KWS detector',
        timers = ['timer'],
        monitors = ['mon1', 'mon2', 'selctr'],
        images = ['det_img'],
        others = [],
        shutter = 'shutter',
        liveinterval = 2.0,
    ),
    det_img = device('nicos.devices.generic.DeviceAlias',
        alias = 'det_img_ge',
        devclass = 'nicos_mlz.kws1.devices.daq.KWSImageChannel',
    ),
)

extended = dict(
    poller_cache_reader = ['shutter', 'gedet_HV'],
)
