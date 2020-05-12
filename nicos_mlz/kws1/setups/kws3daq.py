# -*- coding: utf-8 -*-

description = 'Data acquisition setup for using the KWS3 small detector'
group = 'lowlevel'
display_order = 10

includes = ['counter']
excludes = ['virtual_daq', 'daq']

sysconfig = dict(
    datasinks = ['np_sink', 'yaml_sink'],
)

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

basename = (
    '%(pointcounter)08d_%(pointnumber)04d_'
    '%(proposal)s_%(session.experiment.sample.filename)s_'
    '%(detector)s_%(det.mode)s'
)

devices = dict(
    np_sink = device('nicos.devices.datasinks.text.NPFileSink',
        description = 'Saves image data in text format',
        filenametemplate = [basename + '.det'],
    ),
    yaml_sink = device('nicos_mlz.kws3.devices.yamlformat.YAMLFileSink',
        filenametemplate = [basename + '.yaml'],
    ),
    det_img_jum = device('nicos_mlz.kws1.devices.daq.KWSImageChannel',
        description = 'Image for the high-resolution detector',
        tangodevice = tango_base + 'jumiom/hr_det',
        timer = 'timer',
        fmtstr = '%d (%.1f cps)',
    ),
    det = device('nicos_mlz.kws1.devices.daq.KWSDetector',
        description = 'KWS detector',
        timers = ['timer'],
        monitors = ['mon1', 'mon2', 'mon3', 'selctr'],
        images = ['det_img_jum'],
        postprocess = [],
        shutter = 'shutter',
#        liveinterval = 2.0,
    ),
)
