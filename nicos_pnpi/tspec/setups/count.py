description = 'Count tspec devices'

tango_base = configdata('localconfig.tango_base') + 'count/'

devices = dict(
    timer = device('nicos.devices.generic.VirtualTimer',
                        description = 'timer',
                        ),

    NsRV16115 = device('nicos.devices.entangle.TOFChannel',
                       description = 'USB TOF device of RV161_15',
                       tangodevice = tango_base + 'nv16115/1',
                       lowlevel = True,
                       ),

    mon1 = device('nicos.devices.entangle.CounterChannel',
                  description = 'Monitor',
                  tangodevice = tango_base+'monitors/mon1',
                  type = 'monitor',
                  ),

    det = device('nicos.devices.generic.Detector',
                 description = 'Detector',
                 timers = ['timer'],
                 images = ['NsRV16115']
                 ),

)
