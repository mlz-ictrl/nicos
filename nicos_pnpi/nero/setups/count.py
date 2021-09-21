description = 'Count nero devices'

tango_base = 'tango://server.nero.pnpi:10000/counts/'

devices = dict(
    det1_timer = device('nicos.devices.generic.VirtualTimer',
                        description = 'timer',
                        ),
    det1_mon1 = device('nicos.devices.entangle.CounterChannel',
                       tangodevice = tango_base+'monitors/mon1',
                       description = 'Monitor',
                       type = 'monitor',
                       ),
    fdet1 = device('nicos.devices.entangle.CounterChannel',
                       tangodevice = tango_base+'detectors/fdet1',
                       description = 'Finger detector',
                       type = 'monitor',
                       ),

    det1_img = device('nicos.devices.entangle.ImageChannel',
                      tangodevice = tango_base+'detectors/psd',
                      fmtstr = "%d cts",
                      description = 'PSD Detector',
                      ),

    det = device('nicos.devices.generic.Detector',
                 description = 'Detector',
                 timers = ['det1_timer'],
                 monitors = ['det1_mon', 'fdet1'],
                 images = ['det1_img'],
                 liveinterval = 1,
                 ),
)
