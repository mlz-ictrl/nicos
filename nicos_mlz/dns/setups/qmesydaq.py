#  -*- coding: utf-8 -*-

description = 'qmesydaq channel devices'
group = 'optional'

sysconfig = dict(
    datasinks = ['Histogram', 'Listmode'],
)

nethost = 'mesydaq.dns.frm2'
qm = '//%s/dns/qmesydaq/' % nethost

devices = dict(
    Histogram = device('nicos_mlz.dns.devices.qmesydaqsinks.HistogramSink',
        description = 'Histogram data written via QMesyDAQ',
        timer = 'qtimer',
        subdir = 'psd',
        filenametemplate = ['%(pointcounter)08d.mtxt'],
        detectors = ['qm_det'],
    ),
    Listmode = device('nicos_mlz.dns.devices.qmesydaqsinks.ListmodeSink',
        description = 'Listmode data written via QMesyDAQ',
        timer = 'qtimer',
        liveimage = 'qlive',
        tofchannel = 'dettof',
        subdir = 'psd',
        filenametemplate = ['%(pointcounter)08d.mdat'],
        detectors = ['qm_det'],
    ),
    qmon1 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
        description = 'QMesyDAQ Counter0',
        tacodevice = qm + 'counter0',
        type = 'monitor',
    ),
    qmon2 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
        description = 'QMesyDAQ Counter1',
        tacodevice = qm + 'counter1',
        type = 'monitor',
    ),
    qevents = device('nicos.devices.vendor.qmesydaq.taco.Counter',
        description = 'QMesyDAQ Events channel',
        tacodevice = qm + 'events',
        type = 'counter',
    ),
    qtimer = device('nicos.devices.vendor.qmesydaq.taco.Timer',
        description = 'QMesyDAQ Timer',
        tacodevice = qm + 'timer',
    ),
    qlive = device('nicos_mlz.dns.devices.ImageChannel',
        description = 'QMesyDAQ live image',
        tangodevice = 'tango://phys.dns.frm2:10000/dns/mesy/img',
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
