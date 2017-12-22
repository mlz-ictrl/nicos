description = 'qmesydaq channel devices'

group = 'optional'

qm = '//phys.panda.frm2/panda/qmesydaq/'

devices = dict(
    mon1 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
        description = 'QMesyDAQ Counter0',
        tacodevice = qm + 'counter0',
        fmtstr = '%d',
        type = 'monitor',
    ),
    mon2 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
        description = 'QMesyDAQ Counter1',
        tacodevice = qm + 'counter1',
        fmtstr = '%d',
        type = 'monitor',
    ),
    # mon3 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
    #     description = 'QMesyDAQ Counter2',
    #     tacodevice = qm + 'counter2',
    #     type = 'monitor',
    # ),
    # mon4 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
    #     description = 'QMesyDAQ Counter3',
    #     tacodevice = qm + 'counter3',
    #     type = 'monitor',
    # ),
    # events = device('nicos.devices.vendor.qmesydaq.taco.Counter',
    #     description = 'QMesyDAQ Events channel',
    #     tacodevice = qm + 'events',
    #     fmtstr = '%d',
    #     type = 'counter',
    # ),
    timer = device('nicos.devices.vendor.qmesydaq.taco.Timer',
        description = 'QMesyDAQ Timer',
        tacodevice = qm + 'timer',
    ),
    data = device('nicos.devices.vendor.qmesydaq.taco.MultiCounter',
        description = 'QMesyDAQ Channels',
        tacodevice = qm + 'det',
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
