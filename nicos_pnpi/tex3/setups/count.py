description = 'Count devices'

tango_base = configdata('localconfig.tango_base')

devices = dict(
    det1_timer = device('nicos.devices.generic.VirtualTimer',
                        description = 'timer',
                        ),
    det1_mon1 = device('nicos.devices.entangle.CounterChannel',
                       tangodevice = tango_base+'ns_plx_monitor/ns_plx_monitor/1',
                       description = 'monitor1',
                       type = 'monitor',
                       ),
    det1_mon2 = device('nicos.devices.entangle.CounterChannel',
                       tangodevice = tango_base+'ns_plx_monitor/ns_plx_monitor/2',
                       description = 'monitor2',
                       type = 'monitor',
                       ),


    det1_img = device('nicos.devices.entangle.ImageChannel',
                      tangodevice = tango_base+'nspsd/nspsd/1',
                      fmtstr = "%d cts",
                      description = 'PSD Detector',
                      ),

    det = device('nicos.devices.generic.Detector',
                 description = 'Detector',
                 timers = ['det1_timer'],
                 monitors = ['det1_mon1', 'det1_mon2'],
                 images = ['det1_img'],
                 liveinterval = 1,
                 ),
)
