description = 'qmesydaq channel devices'

group = 'optional'

nethost = 'mesydaq.spheres.frm2'
qm = '//%s/spheres/qmesydaq/' % nethost

devices = dict(
#    mon1 = device('devices.vendor.qmesydaq.taco.Counter',
#                  description = 'QMesyDAQ Counter',
#                  tacodevice = qm + 'counter0',
#                  type = 'monitor',
#                 ),
    events = device('nicos.devices.vendor.qmesydaq.taco.Counter',
                    description = 'QMesyDAQ Events channel',
                    tacodevice = qm + 'events',
                    type = 'counter',
                    ),
    timer = device('nicos.devices.vendor.qmesydaq.taco.Timer',
                   description = 'QMesyDAQ Timer',
                   tacodevice = qm + 'timer',
                  ),
    image = device('nicos.devices.vendor.qmesydaq.taco.Image',
                   description = 'QMesyDAQ MultiChannel Detector',
                   tacodevice = qm + 'image',
                  ),
    det = device('nicos.devices.generic.Detector',
                 description = 'QMesyDAQ Image type Detector',
                 timers = ['timer'],
                 counters = ['events'],
                 monitors = [],
                 images = ['image'],
                ),
)
