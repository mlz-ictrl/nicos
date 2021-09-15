description = 'Virtual count devices'

excludes = ['count']

devices = dict(
    det1_timer = device('nicos.devices.generic.VirtualTimer',
                        description = 'timer',
                        ),
    det1_mon1 = device('nicos.devices.generic.VirtualCounter',
                       description = 'monitor1',
                       type = 'monitor',
                       ),
    det1_mon2 = device('nicos.devices.generic.VirtualCounter',
                       description = 'monitor2',
                       type = 'monitor',
                       ),


    det1_img = device('nicos.devices.generic.VirtualImage',
                      sizes = (128, 128),
                      description = 'PSD Detector'
                      ),

    det = device('nicos.devices.generic.Detector',
                 description = 'Detector',
                 timers = ['det1_timer'],
                 monitors = ['det1_mon1', 'det1_mon2'],
                 images = ['det1_img'],
                 liveinterval = 1,
                 ),
)
