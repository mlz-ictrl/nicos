# -*- coding: utf-8 -*-

description = 'qmesydaq channel devices'

group = 'optional'

sysconfig = dict(datasinks = ['mesysink', 'mesylive'])

tacohost = 'mesydaq.spheres.frm2'
qm = '//%s/spheres/qmesydaq/' % tacohost

devices = dict(
    #    mon1 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
    #                  description = 'QMesyDAQ Counter',
    #                  tacodevice = qm + 'counter0',
    #                  type = 'monitor',
    #                 ),
    events = device('nicos.devices.vendor.qmesydaq.taco.Counter',
        description = 'QMesyDAQ Events channel',
        tacodevice = qm + 'events',
        type = 'counter',
    ),
    mesyimg = device('nicos.devices.vendor.qmesydaq.taco.Image',
        description = 'QMesyDAQ MultiChannel Detector',
        tacodevice = qm + 'det',
    ),
    mesy = device('nicos.devices.generic.Detector',
        description = 'QMesyDAQ Image type Detector',
        timers = ['mesytimer'],
        counters = ['events'],
        images = ['mesyimg'],
        liveinterval = 1.,
    ),
    mesylive = device('nicos_mlz.spheres.devices.mesydaqdatasink.'
        'SpheresMesydaqLiveViewSink',
        description = 'Sends image data to LiveViewWidget',
        detectors = ['mesy']
    ),
    mesysink = device('nicos_mlz.spheres.devices.mesydaqdatasink.'
        'SpheresMesydaqImageSink',
        description = 'DataSink that writes frida readable data',
        filenametemplate = ['%(scancounter)dm%(pointnumber)d'],
        detectors = ['mesy'],
        subdir = 'mesydaq',
    ),
    mesytimer = device('nicos_mlz.spheres.devices.mesydaq.Timer',
        description = 'QMesyDaq timer',
        tacodevice = qm + 'timer'
    ),
)

startupcode = 'SetDetectors(sis, mesy)'
