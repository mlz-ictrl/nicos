# -*- coding: utf-8 -*-

description = 'Virtual detector data acquisition setup'
group = 'lowlevel'
display_order = 10

sysconfig = dict(
    datasinks = ['np_sink', 'yaml_sink'],
)

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

basename = (
    'V_%(pointcounter)08d_%(pointnumber)04d_'
    '%(proposal)s_%(session.experiment.sample.filename)s_'
    '%(detector)s_%(det.mode)s'
)

devices = dict(
    np_sink      = device('kws3.npsaver.NPFileSink',
                          description = 'Saves image data in text format',
                          filenametemplate = [basename + '.det'],
                          lowlevel = True,
                         ),
    yaml_sink    = device('kws3.yamlformat.YAMLFileSink',
                          filenametemplate = [basename + '.yaml'],
                          lowlevel = True,
                         ),

    det_img      = device('devices.generic.DeviceAlias',
                          alias = 'det_img_hrd',
                          devclass = 'kws1.daq.VirtualKWSImageChannel',
                         ),

    detector     = device('kws3.daq.DetSwitcher',
                          description = 'select the active detector',
                          alias = 'det_img',
                          hrd = 'det_img_hrd',
                          vhrd = 'det_img_vhrd',
                         ),

    det_img_hrd  = device('kws1.daq.VirtualKWSImageChannel',
                          description = 'Image for the small KWS detector',
                          sizes = (256, 256),
                         ),

    det_img_vhrd = device('kws1.daq.VirtualKWSImageChannel',
                          description = 'Image for the small KWS detector',
                          sizes = (256, 256),
                         ),

    det_5x5max   = device('kws3.daq.ConvolutionMax',
                          lowlevel = True,
                         ),

    det          = device('kws1.daq.KWSDetector',
                          description = 'KWS detector',
                          timers = ['timer'],
                          monitors = ['mon1', 'mon2'],
                          images = ['det_img'],
                          others = [],
                          shutter = 'shutter',
                          liveinterval = 2.0,
                         ),

    timer      = device('devices.generic.VirtualTimer',
                        description = 'Measurement timer channel',
                        fmtstr = '%.0f',
                       ),

    mon1       = device('devices.generic.VirtualCounter',
                        description = 'Monitor 1 (before selector)',
                        type = 'monitor',
                        fmtstr = '%d',
                        lowlevel = True,
                       ),

    mon2       = device('devices.generic.VirtualCounter',
                        description = 'Monitor 2 (after selector)',
                        type = 'monitor',
                        fmtstr = '%d',
                        lowlevel = True,
                       ),
)

extended = dict(
    poller_cache_reader = ['shutter'],
)

alias_config = {
    'det_img': {'det_img_hrd': 100, 'det_img_vhrd': 90},
}
