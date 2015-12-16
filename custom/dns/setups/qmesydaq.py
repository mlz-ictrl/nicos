#  -*- coding: utf-8 -*-

description = 'qmesydaq channel devices'
group = 'optional'

nethost = 'mesydaq.dns.frm2'
qm = '//%s/test/qmesydaq/' % nethost

devices = dict(
    qmon1 = device('devices.vendor.qmesydaq.taco.Counter',
                   description = 'QMesyDAQ Counter0',
                   tacodevice = qm + 'counter0',
                   type = 'monitor',
                  ),
    qmon2 = device('devices.vendor.qmesydaq.taco.Counter',
                   description = 'QMesyDAQ Counter1',
                   tacodevice = qm + 'counter1',
                   type = 'monitor',
                  ),
    qevents = device('devices.vendor.qmesydaq.taco.Counter',
                     description = 'QMesyDAQ Events channel',
                     tacodevice = qm + 'events',
                     type = 'counter',
                     ),
    qtimer = device('devices.vendor.qmesydaq.taco.Timer',
                    description = 'QMesyDAQ Timer',
                    tacodevice = qm + 'timer',
                   ),
#   files = device('devices.vendor.qmesydaq.Filenames',
#                  description = 'QMesyDAQ Filenames',
#                  tacodevice = qm + 'det',
#                 ),
    qm_det = device('devices.generic.Detector',
                    description = 'QMesyDAQ MultiChannel Detector',
                    timers = ['qtimer'],
                    counters = ['qevents'],
                    monitors = ['qmon1', 'qmon2'],
                    fileformats = [],
                    subdir = '',
                   ),
)
