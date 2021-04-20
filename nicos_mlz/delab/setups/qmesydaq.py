description = 'testing qmesydaq'

group = 'optional'

excludes = []

sysconfig = dict(
    datasinks = ['LiveViewSink'],
)

tango_base = 'tango://localhost:10000/test/qmesydaq/'

devices = dict(
    # RAWFileSaver = device('nicos.devices.datasinks.RawImageSink',
    #     description = 'Saves image data in RAW format',
    #     filenametemplate = [
    #         '%(proposal)s_%(pointcounter)06d.raw',
    #         '%(proposal)s_%(scancounter)s_'
    #         '%(pointcounter)s_%(pointnumber)s.raw'],
    #     subdir = 'QMesyDAQ2',
    #     lowlevel = True,
    # ),
    LiveViewSink = device('nicos.devices.datasinks.LiveViewSink',
        description = 'Sends image data to LiveViewWidget',
    ),
    qm_ctr0 = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ Counter0',
        tangodevice = tango_base + 'counter0',
        type = 'counter',
        lowlevel = True,
    ),
    qm_ctr1 = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ Counter1',
        tangodevice = tango_base + 'counter1',
        type = 'counter',
        lowlevel = True,
    ),
    qm_ctr2 = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ Counter2',
        tangodevice = tango_base + 'counter2',
        type = 'monitor',
        lowlevel = True,
    ),
    qm_ctr3 = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ Counter3',
        tangodevice = tango_base + 'counter3',
        type = 'monitor',
        lowlevel = True,
    ),
    qm_ev = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ Events channel',
        tangodevice = tango_base + 'events',
        type = 'counter',
        lowlevel = True,
    ),
    qm_timer = device('nicos.devices.entangle.TimerChannel',
        description = 'QMesyDAQ Timer',
        tangodevice = tango_base + 'timer',
    ),
    mesytec = device('nicos.devices.generic.Detector',
        description = 'QMesyDAQ Image type Detector',
        timers = ['qm_timer'],
        counters = [
            'qm_ev',
            # 'qm_ctr0',  'qm_ctr2'
        ],
        monitors = [
            #'qm_ctr1',  'qm_ctr3'
        ],
        others = [],
    ),
)

startupcode = '''
SetDetectors(mesytec)
'''
