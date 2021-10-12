description = 'qmesydaq channel devices'

group = 'lowlevel'
display_order = 70

qm_base = 'tango://phys.panda.frm2:10000/qm/qmesydaq/'

devices = dict(
    mon1 = device('nicos.devices.vendor.qmesydaq.tango.CounterChannel',
        description = 'QMesyDAQ Counter0',
        tangodevice = qm_base + 'counter0',
        type = 'monitor',
    ),
    mon2 = device('nicos.devices.vendor.qmesydaq.tango.CounterChannel',
        description = 'QMesyDAQ Counter1',
        tangodevice = qm_base + 'counter1',
        type = 'monitor',
    ),
    timer = device('nicos.devices.vendor.qmesydaq.tango.TimerChannel',
        description = 'QMesyDAQ Timer',
        tangodevice = qm_base + 'timer',
    ),
    data = device('nicos.devices.vendor.qmesydaq.tango.MultiCounter',
        description = 'QMesyDAQ Channels',
        tangodevice = qm_base + 'image',
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'QMesyDAQ MultiChannel Detector',
        timers = ['timer'],
        counters = ['data'],
        monitors = ['mon1', 'mon2'],
    ),
)

startupcode = '''
SetDetectors(det)
'''
