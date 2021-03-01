# -*- coding: utf-8 -*-

description = 'detector setup'
group = 'basic'

includes = [
    'analyzer',
    'beamstop',
    'treff',
]

sysconfig = dict(
    datasinks = ['NPGZFileSink', 'YAMLSaver', 'LiveViewSink'],
)

basename = '%(proposal)s_%(session.experiment.sample.filename)s_'
scanbasename = basename + '%(scancounter)08d_%(pointnumber)08d'
countbasename = basename + '%(pointpropcounter)010d'

devices = dict(
    NPGZFileSink = device('nicos.devices.datasinks.text.NPGZFileSink',
        description = 'Saves image data in numpy text format',
        filenametemplate = [
            scanbasename + '.gz',
            countbasename + '.gz',
        ],
    ),
    YAMLSaver = device('nicos_mlz.maria.devices.yamlformat.YAMLFileSink',
        filenametemplate = [
            scanbasename + '.yaml',
            countbasename + '.yaml',
        ],
    ),
    LiveViewSink = device('nicos.devices.datasinks.LiveViewSink',
        description = 'Sends image data to LiveViewWidget',
    ),
    detimg = device('nicos_demo.vtreff.devices.detector.McStasImage',
        description = 'Detector image',
        ratio = 1.6e6,
        size = (256, 256),
        fmtstr = '%d',
        unit = 'cts',
        lowlevel = True,
        beamstop = 'beamstop',
        sample_y = 'sample_y',
        sample_x = 'sample_x',
        sample_z = 'sample_z',
        omega = 'omega',
        chi = 'chi',
        phi = 'phi',
        detarm = 'detarm',
        s1 = 's1',
        s2 = 's2',
        sample = 'Sample',
    ),
    full = device('nicos.devices.generic.RateChannel',
        description = 'Full detector cts and rate',
    ),
    roi1 = device('nicos.devices.generic.RectROIChannel',
        description = 'ROI 1',
        roi = (122, 50, 12, 140),
    ),
    roi2 = device('nicos.devices.generic.RectROIChannel',
        description = 'ROI 2',
        roi = (122, 119, 12, 18),
    ),
    roi_pol = device('nicos.devices.generic.RectROIChannel',
        description = 'ROI 1',
        roi = (122, 76, 12, 114),
    ),
    timer = device('nicos.devices.mcstas.McStasTimer',
        description='McStas virtual neutron counts timer channel',
        mcstasimage = 'detimg',
    ),
    det = device('nicos_mlz.maria.devices.detector.MariaDetector',
        description = 'Jumiom detector',
        shutter = 'expshutter',
        timers = ['timer'],
        monitors = ['mon0', 'mon1'],
        images = ['detimg'],
        counters = ['roi1', 'roi2', 'roi_pol', 'full'],
        postprocess = [
            ('roi1', 'detimg'),
            ('roi2', 'detimg'),
            ('roi_pol', 'detimg'),
            ('full', 'detimg', 'timer')
        ],
        liveinterval = .5,
    ),
)

startupcode = """
SetDetectors(det)
"""
