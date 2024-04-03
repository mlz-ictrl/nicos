description = 'qmesydaq channel devices'
group = 'optional'

sysconfig = dict(
    datasinks = ['mesysink', 'mesylive']
)

qm = 'tango://mesydaq.spheres.frm2:10000/spheres/qmesydaq/'

devices = dict(
    #    mon1 = device('nicos.devices.vendor.qmesydaq.tango.CounterChannel',
    #                  description = 'QMesyDAQ Counter',
    #                  tangodevice = qm + 'counter0',
    #                  type = 'monitor',
    #                 ),
    events = device('nicos.devices.vendor.qmesydaq.tango.CounterChannel',
        description = 'QMesyDAQ Events channel',
        tangodevice = qm + 'events',
        type = 'counter',
    ),
    mesyimg = device('nicos.devices.vendor.qmesydaq.tango.ImageChannel',
        description = 'QMesyDAQ MultiChannel Detector',
        tangodevice = qm + 'det',
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
        tangodevice = qm + 'timer'
    ),
)

startupcode = 'SetDetectors(sis, mesy)'
