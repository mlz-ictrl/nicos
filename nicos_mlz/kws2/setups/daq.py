# -*- coding: utf-8 -*-

description = 'Detector data acquisition setup'
group = 'lowlevel'
display_order = 25

includes = ['counter']
excludes = ['virtual_daq']

sysconfig = dict(
    datasinks = ['kwsformat', 'LiveViewSink'],
)

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    kwsformat = device('nicos_mlz.kws2.devices.kwsfileformat.KWSFileSink',
        transpose = True,
        detectors = ['det'],
    ),
    yamlformat = device('nicos_mlz.kws2.devices.yamlformat.YAMLFileSink',
        detectors = ['det'],
    ),
    LiveViewSink = device("nicos.devices.datasinks.LiveViewSink",
        description = "Sends image data to LiveViewWidget",
    ),
    det_mode = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Current detector mode',
        device = 'det_img',
        parameter = 'mode',
    ),
    det_img_ge = device('nicos_mlz.kws1.devices.daq.GEImageChannel',
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
    det_roi = device('nicos_mlz.kws1.devices.daq.ROIRateChannel',
        description = 'Counts inside beamstop area',
        bs_x = 'beamstop_x',
        bs_y = 'beamstop_y',
        timer = 'timer',
        xscale = (0.125, 72),
        yscale = (0.125, 62),
        size = (10, 10),
    ),
    det = device('nicos_mlz.kws1.devices.daq.KWSDetector',
        description = 'KWS detector',
        timers = ['timer'],
        monitors = ['mon1', 'mon2', 'selctr'],
        images = ['det_img'],
        counters = ['det_roi'],
        others = [],
        postprocess = [('det_roi', 'det_img')],
        shutter = 'shutter',
        liveinterval = 2.0,
    ),
    det_img = device('nicos.devices.generic.DeviceAlias',
        alias = 'det_img_ge',
        devclass = 'nicos_mlz.kws1.devices.daq.KWSImageChannel',
    ),
)

extended = dict(
    poller_cache_reader = ['shutter', 'gedet_HV', 'beamstop_x', 'beamstop_y'],
    representative = 'det_img',
)
