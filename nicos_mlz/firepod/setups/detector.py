description = 'FirePOD detector'

group = 'lowlevel'

includes = [
    'hv1', 'hv2', 'hv3', 'hv4', 'hv5', 'hv6', 'hv7', 'hv8',
]

sysconfig = dict(
    datasinks = ['histogram', ],  # 'listmode'],
)

tango_host = 'firepoddet.erwin.frm2.tum.de'

tango_base = f'tango://{tango_host}:10000/qm/qmesydaq/'

devices = dict(
    hv = device('nicos_mlz.firepod.devices.detectorhv.DetectorHV',
        description = 'Detector HV switch',
        channels = [
            'det1_hv',
            'det2_hv',
            'det3_hv',
            'det4_hv',
            'det5_hv',
            'det6_hv',
            'det7_hv',
            'det8_hv',
        ],
    ),
    mon = device('nicos.devices.vendor.qmesydaq.tango.CounterChannel',
        description = 'Monitor 1',
        tangodevice = tango_base + 'counter0',
        type = 'monitor',
        visibility = (),
    ),
    events = device('nicos.devices.vendor.qmesydaq.tango.CounterChannel',
        description = 'Event counter',
        tangodevice = tango_base + 'events',
        type = 'other',
        visibility = (),
    ),
    image = device('nicos.devices.vendor.qmesydaq.tango.ImageChannel',
        description = 'Image',
        tangodevice = tango_base + 'image',
        visibility = (),
    ),
    tim1 = device('nicos.devices.vendor.qmesydaq.tango.TimerChannel',
        description = 'Timer',
        tangodevice = tango_base + 'timer',
        visibility = (),
    ),
    basedet = device('nicos.devices.generic.Detector',
        description = 'Classical detector with single channels',
        timers = ['tim1'],
        monitors = ['mon'],
        images = ['image'],
        maxage = 86400,
        pollinterval = None,
        liveinterval = 1.0,
        # visibility = (),
    ),
    histogram = device('nicos_mlz.devices.datasinks.qmesydaq.HistogramSink',
        description = 'Histogram data written via QMesyDAQ',
        image = 'image',
        subdir = 'mtxt',
        filenametemplate = ['%(pointcounter)08d.mtxt'],
    ),
    listmode = device('nicos_mlz.devices.datasinks.qmesydaq.ListmodeSink',
        description = 'Listmode data written via QMesyDAQ',
        image = 'image',
        subdir = 'list',
        filenametemplate = ['%(pointcounter)08d.mdat'],
    ),
)

startupcode = """
SetDetectors(basedet)
"""
