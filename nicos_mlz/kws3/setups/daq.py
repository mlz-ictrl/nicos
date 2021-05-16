# -*- coding: utf-8 -*-

description = 'Detector data acquisition setup'
group = 'lowlevel'
display_order = 10

includes = ['counter']
excludes = ['virtual_daq']

sysconfig = dict(
    datasinks = ['yamlformat', 'binaryformat'],
)

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

basename = (
    '%(pointcounter)08d_%(pointnumber)04d_'
    '%(proposal)s_%(session.experiment.sample.filename)s_'
    '%(detector)s_%(det.mode)s'
)

NAME_TEMPLATE = (
    '%(pointcounter)08d_%(pointnumber)04d_'
    '%(proposal)s_'
    '%(session.experiment.sample.filename)s_'
    'C%(resolution)s_'
    'D%(detector)s_'
    'L%(selector)s_'
    'P%(polarizer)s_'
    '%(det_img.mode)s.'
    '%(session.instrument.name)s'
)

devices = dict(
    yamlformat = device('nicos_mlz.kws3.devices.yamlformat.YAMLFileSink',
        detectors = ['det'],
        filenametemplate = [NAME_TEMPLATE + '.yaml'],
    ),
    binaryformat = device('nicos_mlz.kws1.devices.yamlformat.BinaryArraySink',
        detectors = ['det'],
        filenametemplate = [NAME_TEMPLATE + '.array.gz'],
    ),
    det_img = device('nicos.devices.generic.DeviceAlias',
        alias = 'det_img_hrd',
        devclass = 'nicos_mlz.kws1.devices.daq.KWSImageChannel',
    ),
    detector = device('nicos_mlz.kws3.devices.daq.DetSwitcher',
        description = 'select the active detector',
        alias = 'det_img',
        hrd = 'det_img_hrd',
        vhrd = 'det_img_vhrd',
    ),
    det_img_hrd = device('nicos_mlz.kws1.devices.daq.KWSImageChannel',
        description = 'Image for the high-resolution detector',
        tangodevice = tango_base + 'jumiom/hr_det',
        timer = 'timer',
        fmtstr = '%d (%.1f cps)',
        lowlevel = False,
    ),
    det_img_vhrd = device('nicos_mlz.kws1.devices.daq.KWSImageChannel',
        description = 'Image for the very high-resolution detector',
        tangodevice = tango_base + 'jumiom/vhr_det',
        timer = 'timer',
        fmtstr = '%d (%.1f cps)',
        lowlevel = False,
    ),
    det_5x5max = device('nicos_mlz.kws3.devices.daq.ConvolutionMax',
        lowlevel = True,
    ),
    det_roi = device('nicos_mlz.kws3.devices.daq.ROIChannel',
        description = 'Counts in ROI',
        lowlevel = False,
    ),
    det = device('nicos_mlz.kws1.devices.daq.KWSDetector',
        description = 'KWS detector',
        timers = ['timer'],
        monitors = ['mon1', 'mon2'],
        images = ['det_img'],
        counters = ['det_roi'], # ['det_5x5max'],
        others = [],
#        postprocess = [],
        postprocess = [('det_roi', 'det_img')],
#        postprocess = [('det_5x5max', 'det_img')],
        shutter = None,
        liveinterval = 2.0,
    ),
)

extended = dict(
    representative = 'det_img',
)

alias_config = {
    'det_img': {'det_img_hrd': 100, 'det_img_vhrd': 90},
}
