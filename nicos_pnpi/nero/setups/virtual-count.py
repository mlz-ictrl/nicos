description = 'Count nero devices'

excludes = ['count']

devices = dict(
    det1_timer = device('nicos.devices.generic.VirtualTimer',
                        description = 'timer',
                        ),
    det1_mon1 = device('nicos.devices.generic.VirtualCounter',
                       description = 'Monitor',
                       type = 'monitor',
                       ),
    fdet1 = device('nicos.devices.generic.VirtualCounter',
                       description = 'Finger detector',
                       type = 'monitor',
                       ),

    det1_img = device('nicos.devices.generic.VirtualImage',
                      sizes = (128, 128),
                      fmtstr = "%d cts",
                      description = 'PSD Detector',
                      ),

    det = device('nicos.devices.generic.Detector',
                 description = 'Detector',
                 timers = ['det1_timer'],
                 monitors = ['det1_mon1', 'fdet1'],
                 images = ['det1_img'],
                 liveinterval = 1,
                 ),
)
