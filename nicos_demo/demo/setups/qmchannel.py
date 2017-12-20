description = 'qmesydaq channel devices'

group = 'optional'

excludes = ['detector', 'sans', 'refsans', 'vtof', 'pgaa']

nethost = 'taco61.ictrl.frm2'
qm = '//%s/test/qmesydaq/' % nethost

devices = dict(
    mon1 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
        description = 'QMesyDAQ Counter0',
        tacodevice = qm + 'counter0',
        type = 'monitor',
    ),
    mon2 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
        description = 'QMesyDAQ Counter1',
        tacodevice = qm + 'counter1',
        type = 'monitor',
    ),
    mon3 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
        description = 'QMesyDAQ Counter2',
        tacodevice = qm + 'counter2',
        type = 'monitor',
    ),
    mon4 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
        description = 'QMesyDAQ Counter3',
        tacodevice = qm + 'counter3',
        type = 'monitor',
    ),
    events = device('nicos.devices.vendor.qmesydaq.taco.Counter',
        description = 'QMesyDAQ Events channel',
        tacodevice = qm + 'events',
        type = 'counter',
    ),
    timer = device('nicos.devices.vendor.qmesydaq.taco.Timer',
        description = 'QMesyDAQ Timer',
        tacodevice = qm + 'timer',
    ),
    data = device('nicos.devices.vendor.qmesydaq.taco.MultiCounter',
        description = 'QMesyDAQ Counter channels',
        tacodevice = qm + 'det',
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'QMesyDAQ MultiChannel Detector',
        timers = ['timer'],
        counters = ['events', 'data'],
        monitors = ['mon1', 'mon2', 'mon3', 'mon4'],
    ),
)

startupcode = '''
SetDetectors(det)
'''
