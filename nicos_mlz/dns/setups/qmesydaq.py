#  -*- coding: utf-8 -*-

description = 'qmesydaq channel devices'
group = 'optional'

sysconfig = dict(
    datasinks = ['Histogram', 'Listmode'],
)

tango_base = 'tango://phys.dns.frm2:10000/'
qm_base = tango_base + 'qm/qmesydaq/'

devices = dict(
    Histogram = device('nicos_mlz.dns.devices.qmesydaqsinks.HistogramSink',
        description = 'Histogram data written via QMesyDAQ',
        image = 'qevents',
        subdir = 'psd',
        filenametemplate = ['%(pointcounter)08d.mtxt'],
        detectors = ['qm_det'],
    ),
    Listmode = device('nicos_mlz.dns.devices.qmesydaqsinks.ListmodeSink',
        description = 'Listmode data written via QMesyDAQ',
        image = 'qevents',
        liveimage = 'qlive',
        tofchannel = 'dettof',
        subdir = 'psd',
        filenametemplate = ['%(pointcounter)08d.mdat'],
        detectors = ['qm_det'],
    ),
    qmon1 = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ Counter0',
        tangodevice = qm_base + 'counter0',
        type = 'monitor',
    ),
    qmon2 = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ Counter1',
        tangodevice = qm_base + 'counter1',
        type = 'monitor',
    ),
    qevents = device('nicos_mlz.dns.devices.qmesydaqsinks.ImageCounterChannel',
        description = 'QMesyDAQ Events channel',
        tangodevice = qm_base + 'image',
        type = 'counter',
    ),
    qtimer = device('nicos.devices.entangle.TimerChannel',
        description = 'QMesyDAQ Timer',
        tangodevice = qm_base + 'timer',
    ),
    qlive = device('nicos_mlz.dns.devices.ImageChannel',
        description = 'QMesyDAQ live image',
        tangodevice = tango_base + 'dns/mesy/img',
    ),
    qm_det = device('nicos_mlz.dns.devices.detector.DNSDetector',
        description = 'QMesyDAQ MultiChannel Detector',
        flipper = 'flipper',
        timers = ['qtimer'],
        counters = ['qevents'],
        monitors = ['qmon1', 'qmon2'],
        images = ['qlive'],
    ),
)

extended = dict(
    poller_cache_reader = ['flipper'],
    representative = 'qm_det',
)

startupcode = '''
AddDetector(qm_det)
'''
