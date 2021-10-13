description = 'Small charm detector'

group = 'optional'

tango_host = 'qmesydaq-test.del.frm2.tum.de'

tango_base = 'tango://%s:10000/qm/qmesydaq/' % tango_host

devices = dict(
    ds_mon1 = device('nicos.devices.vendor.qmesydaq.tango.CounterChannel',
        description = 'Monitor 1 at small charm detector',
        tangodevice = tango_base + 'counter0',
        type = 'monitor',
    ),
    ds_events = device('nicos.devices.vendor.qmesydaq.tango.CounterChannel',
        description = 'Event counter at small charm detector',
        tangodevice = tango_base + 'events',
        type = 'other',
    ),
    ds_image = device('nicos.devices.vendor.qmesydaq.tango.ImageChannel',
        description = 'Image at small charm detector',
        tangodevice = tango_base + 'image',
    ),
    ds_timer = device('nicos.devices.vendor.qmesydaq.tango.TimerChannel',
        description = 'Timer at small charm detector',
        tangodevice = tango_base + 'timer',
    ),
    ds_det = device('nicos.devices.generic.Detector',
        description = 'Small charm detector',
        images = ['ds_image'],
        monitors = ['ds_mon1'],
        timers = ['ds_timer'],
        liveinterval = 1.0,
    ),
)
