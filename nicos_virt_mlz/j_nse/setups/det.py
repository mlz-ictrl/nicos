description = 'Denex detector setup'
group = 'basic'

includes = [
    'ccmotors',
    'counter',
    'motors',
    'physics',
    'power',
    'spsanalog',
    'thermojet',
]

sysconfig = dict(
    datasinks = ['LiveViewSink', 'NPGZFileSink'],
)

basename = '%(proposal)s_'
scanbasename = basename + '%(scancounter)08d_%(pointnumber)08d'
countbasename = basename + '%(pointpropcounter)010d'

devices = dict(
    LiveViewSink = device(
        'nicos.devices.datasinks.LiveViewSink',
        description = 'Sends image data to LiveViewWidget',
    ),
    NPGZFileSink = device(
        'nicos.devices.datasinks.text.NPGZFileSink',
        description = 'Saves image data in compressed numpy text format',
        filenametemplate = [
            scanbasename + '.gz',
            countbasename + '.gz',
        ],
    ),
    detimg = device(
        'nicos.devices.generic.VirtualImage',
        visibility = (),
        size = (32, 32),
    ),
    roi1 = device(
        'nicos.devices.generic.RectROIChannel',
        description = 'ROI 1',
        roi = (7, 7, 18, 18),
    ),
    det = device(
        'nicos.devices.generic.detector.Detector',
        description = 'Denex detector',
        timers = ['timer'],
        monitors = ['monbgr', 'mon1'],
        images = ['detimg'],
        counters = ['roi1',],
        postprocess = [
            ('roi1', 'detimg'),
        ],
        liveinterval = 0.5,
    ),
    nsedet = device(
        'nicos_mlz.j_nse.devices.jnse.ScanningDetector',
        description = 'High-level JNSE detector',
        detector = 'det',
        lmbda = 'Lambda',
        tau = 't_nom',
        pha1 = 'pow20',
        pi = 'pow03',
        pi21 = 'pow02',
        pi22 = 'pow04',
    ),
)

startupcode = 'SetDetectors(det)'
