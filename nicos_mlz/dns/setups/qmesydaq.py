#  -*- coding: utf-8 -*-

description = 'qmesydaq channel devices'
group = 'optional'

nethost = 'mesydaq.dns.frm2'
qm = '//%s/dns/qmesydaq/' % nethost

devices = dict(
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
#   files = device('nicos.devices.vendor.qmesydaq.Filenames',
#                  description = 'QMesyDAQ Filenames',
#                  tacodevice = qm + 'det',
#                 ),
    qm_det = device('nicos.devices.generic.Detector',
                    description = 'QMesyDAQ MultiChannel Detector',
                    timers = ['qtimer'],
                    counters = ['qevents'],
                    monitors = ['qmon1', 'qmon2'],
                   ),
)
