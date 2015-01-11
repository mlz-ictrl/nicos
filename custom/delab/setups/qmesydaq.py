description = 'testing qmesydaq'

group = 'optional'

excludes = ['acqiris',]

nethost = 'localhost'

devices = dict(
    # RAWFileSaver      = device('nicos.devices.fileformats.RAWFileFormat',
    #                          description = 'Saves image data in RAW format',
    #                          filenametemplate = ['%(proposal)s_%(counter)06d.raw',
    #                          '%(proposal)s_%(session.experiment.lastscan)s_'
    #                          '%(counter)s_%(scanpoint)s.raw'],
    #                          lowlevel = True,
    #                         ),
    LiveViewSink = device('nicos.devices.fileformats.LiveViewSink',
                          description = 'Sends image data to LiveViewWidget',
                          filenametemplate = [''],
                          lowlevel = True,
                         ),
    qm_ctr0 = device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                     description = 'QMesyDAQ Counter0',
                     tacodevice = '//%s/test/qmesydaq/counter0' % nethost,
                     type = 'counter',
                     lowlevel = True,
                    ),
    qm_ctr1 = device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                     description = 'QMesyDAQ Counter1',
                     tacodevice = '//%s/test/qmesydaq/counter1' % nethost,
                     type = 'counter',
                     lowlevel = True,
                    ),
    qm_ctr2 = device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                     description = 'QMesyDAQ Counter2',
                     tacodevice = '//%s/test/qmesydaq/counter2' % nethost,
                     type = 'monitor',
                     lowlevel = True,
                    ),
    qm_ctr3= device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                     description = 'QMesyDAQ Counter3',
                     tacodevice = '//%s/test/qmesydaq/counter3' % nethost,
                     type = 'monitor',
                     lowlevel = True,
                    ),
    qm_ev  = device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                     description = 'QMesyDAQ Events channel',
                     tacodevice = '//%s/test/qmesydaq/events' % nethost,
                     type = 'counter',
                     lowlevel = True,
                    ),
    qm_timer = device('nicos.devices.vendor.qmesydaq.QMesyDAQTimer',
                     description = 'QMesyDAQ Timer',
                     tacodevice = '//%s/test/qmesydaq/timer' % nethost,
                    ),
    mesytec = device('nicos.devices.vendor.qmesydaq.QMesyDAQImage',
                     description = 'QMesyDAQ Image type Detector',
                     tacodevice = '//%s/test/qmesydaq/det' % nethost,
                     events = 'qm_ev',
                     timer = 'qm_timer',
                     counters = [
                     # 'qm_ctr0',  'qm_ctr2'
                     ],
                     monitors = [
                     #'qm_ctr1',  'qm_ctr3'
                     ],
                     fileformats = [
#                                   'RAWFileSaver',
                                    'LiveViewSink',
                                   ],
                     readout = 'none',
                     subdir = 'QMesyDAQ2',
                    ),
)

startupcode = """
SetDetectors(mesytec)
"""
