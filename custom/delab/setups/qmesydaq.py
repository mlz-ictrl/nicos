description = 'testing qmesydaq'

group = 'optional'

excludes = ['acqiris',]

nethost = 'localhost'

devices = dict(
    # RAWFileSaver      = device('devices.datasinks.RawImageSink',
    #                          description = 'Saves image data in RAW format',
    #                          filenametemplate = ['%(proposal)s_%(counter)06d.raw',
    #                          '%(proposal)s_%(session.experiment.lastscan)s_'
    #                          '%(counter)s_%(scanpoint)s.raw'],
    #                          lowlevel = True,
    #                         ),
    LiveViewSink = device('devices.datasinks.LiveViewSink',
                          description = 'Sends image data to LiveViewWidget',
                          filenametemplate = [''],
                          lowlevel = True,
                         ),
    qm_ctr0 = device('devices.vendor.qmesydaq.taco.Counter',
                     description = 'QMesyDAQ Counter0',
                     tacodevice = '//%s/test/qmesydaq/counter0' % nethost,
                     type = 'counter',
                     lowlevel = True,
                    ),
    qm_ctr1 = device('devices.vendor.qmesydaq.taco.Counter',
                     description = 'QMesyDAQ Counter1',
                     tacodevice = '//%s/test/qmesydaq/counter1' % nethost,
                     type = 'counter',
                     lowlevel = True,
                    ),
    qm_ctr2 = device('devices.vendor.qmesydaq.taco.Counter',
                     description = 'QMesyDAQ Counter2',
                     tacodevice = '//%s/test/qmesydaq/counter2' % nethost,
                     type = 'monitor',
                     lowlevel = True,
                    ),
    qm_ctr3 = device('devices.vendor.qmesydaq.taco.Counter',
                     description = 'QMesyDAQ Counter3',
                     tacodevice = '//%s/test/qmesydaq/counter3' % nethost,
                     type = 'monitor',
                     lowlevel = True,
                    ),
    qm_ev  = device('devices.vendor.qmesydaq.taco.Counter',
                     description = 'QMesyDAQ Events channel',
                     tacodevice = '//%s/test/qmesydaq/events' % nethost,
                     type = 'counter',
                     lowlevel = True,
                    ),
    qm_timer = device('devices.vendor.qmesydaq.taco.Timer',
                     description = 'QMesyDAQ Timer',
                     tacodevice = '//%s/test/qmesydaq/timer' % nethost,
                    ),
    mesytec = device('devices.generic.Detector',
                     description = 'QMesyDAQ Image type Detector',
                     timers = ['qm_timer'],
                     counters = ['qm_ev',
                     # 'qm_ctr0',  'qm_ctr2'
                     ],
                     monitors = [
                     #'qm_ctr1',  'qm_ctr3'
                     ],
                     others = [],
                     fileformats = [
#                                   'RAWFileSaver',
                                    'LiveViewSink',
                                   ],
                     subdir = 'QMesyDAQ2',
                    ),
)

startupcode = '''
SetDetectors(mesytec)
'''
