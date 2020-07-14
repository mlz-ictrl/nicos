description = 'qmesydaq devices for REFSANS'

# to be included by refsans ?
group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = 'tango://detector01.refsans.frm2.tum.de:10000/qm/qmesydaq/'

sysconfig = dict(
    datasinks = ['Listmode'],
)

devices = dict(
    # BerSANSFileSaver = device('nicos_mlz.sans1.devices.bersans.BerSANSImageSink',
    #     description = 'Saves image data in BerSANS format',
    #     filenametemplate = [
    #         'D%(pointcounter)07d.001', '/data_user/D%(pointcounter)07d.001'
    #     ],
    #     subdir = 'bersans',
    # ),
    Listmode = device('nicos_mlz.devices.qmesydaqsinks.ListmodeSink',
        description = 'Listmode data written via QMesyDAQ',
        image = 'image',
        subdir = 'list',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.mdat'],
    ),
    LiveViewSink = device('nicos.devices.datasinks.LiveViewSink',
        description = 'Sends image data to LiveViewWidget',
    ),
    mon1 = device('nicos.devices.tango.CounterChannel',
        description = 'QMesyDAQ Counter0',
        tangodevice = tango_base + 'counter0',
        type = 'monitor',
    ),
    mon2 = device('nicos.devices.tango.CounterChannel',
        description = 'QMesyDAQ Counter1',
        tangodevice = tango_base + 'counter1',
        type = 'monitor',
    ),
    # qm_ctr2 = device('nicos.devices.tango.CounterChannel',
    #     description = 'QMesyDAQ Counter2',
    #     tangodevice = tango_base + 'counter2',
    #     type = 'monitor',
    # ),
    # qm_ctr3 = device('nicos.devices.tango.CounterChannel',
    #     description = 'QMesyDAQ Counter3',
    #     tangodevice = tango_base + 'counter3',
    #     type = 'monitor',
    # ),
    # qm_ev = device('nicos.devices.tango.CounterChannel',
    #     description = 'QMesyDAQ Events channel',
    #     tangodevice = tango_base + 'events',
    #     type = 'counter',
    # ),
    timer = device('nicos.devices.tango.TimerChannel',
        description = 'QMesyDAQ Timer',
        tangodevice = tango_base + 'timer',
    ),
    image = device('nicos.devices.vendor.qmesydaq.tango.ImageChannel',
        description = 'QMesyDAQ Image',
        tangodevice = tango_base + 'image',
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'QMesyDAQ Image type Detector1',
        timers = ['timer'],
        monitors = ['mon1', 'mon2'],
        images = ['image'],
    ),
)

startupcode = '''
SetDetectors(det)
'''
