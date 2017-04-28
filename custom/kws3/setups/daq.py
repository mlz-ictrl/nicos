# -*- coding: utf-8 -*-

description = 'Detector data acquisition setup'
group = 'lowlevel'
display_order = 10

includes = ['counter']
excludes = ['virtual_daq']

sysconfig = dict(
    datasinks = ['npgz_sink', 'yaml_sink'],
)

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

basename = (
    '%(pointcounter)08d_%(pointnumber)04d_'
    '%(proposal)s_%(session.experiment.sample.filename)s_'
    '%(detector)s_%(det.mode)s'
)

devices = dict(
    npgz_sink    = device('maria.npsaver.NPGZFileSink',
                          description = 'Saves image data in text format',
                          filenametemplate = [basename + '.gz'],
                          lowlevel = True,
                         ),
    yaml_sink    = device('maria.yamlformat.YAMLFileSink',
                          filenametemplate = [basename + '.yaml'],
                          lowlevel = True,
                         ),

    det_img      = device('devices.generic.DeviceAlias',
                          alias = 'det_img_ge',
                          devclass = 'nicos.kws1.daq.KWSImageChannel',
                         ),

    detector     = device('kws3.daq.DetSwitcher',
                          description = 'select the active detector',
                          alias = 'det_img',
                          hrd = 'det_img_hrd',
                          vhrd = 'det_img_vhrd',
                         ),

    det_img_hrd  = device('kws1.daq.KWSImageChannel',
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

    det          = device('kws1.daq.KWSDetector',
                          description = 'KWS detector',
                          timers = ['timer'],
                          monitors = ['mon1', 'mon2'],
                          images = ['det_img'],
                          others = [],
                          shutter = 'shutter',
                          liveinterval = 2.0,
                         ),
)

extended = dict(
    poller_cache_reader = ['shutter'],
)

alias_config = {
    'det_img': {'det_img_hrd': 100, 'det_img_vhrd': 90},
}
