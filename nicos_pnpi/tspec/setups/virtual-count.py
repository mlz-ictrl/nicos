description = 'Count tspec devices'

excludes = ['count']

devices = dict(
    timer = device('nicos.devices.generic.VirtualTimer',
                   description = 'timer',
                   ),

    NsRV16115 = device('nicos.devices.generic.VirtualImage',
                       description = 'USB TOF device of RV161_15',
                       lowlevel = True,
                       ),

    mon1 = device('nicos.devices.generic.VirtualCounter',
                  description = 'Monitor',
                  type = 'monitor',
                  ),

    det = device('nicos.devices.generic.Detector',
                 description = 'Detector',
                 timers = ['timer'],
                 monitors = ['mon1'],
                 images = ['NsRV16115'],
                 ),

)
