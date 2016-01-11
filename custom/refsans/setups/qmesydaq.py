description = 'qmesydaq devices for REFSANS'

# to be included by refsans ?
group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test/qmesydaq' % nethost

devices = dict(
    BerSANSFileSaver  = device('sans1.bersans.BerSANSFileFormat',
                               description = 'Saves image data in BerSANS format',
                               filenametemplate = ['D%(counter)07d.001',
                                                   '/data_user/D%(counter)07d.001'],
                               flipimage = 'none',
                               lowlevel = True,
                              ),
    #~ LiveViewSink = device('devices.fileformats.LiveViewSink',
                          #~ description = 'Sends image data to LiveViewWidget',
                          #~ filenametemplate=[],
                          #~ lowlevel = True,
                         #~ ),
    mon1 = device('devices.vendor.qmesydaq.Counter',
                  description = 'QMesyDAQ Counter0',
                  tacodevice = '%s/counter0' % tacodev,
                  type = 'monitor',
                 ),
    mon2 = device('devices.vendor.qmesydaq.Counter',
                  description = 'QMesyDAQ Counter1',
                  tacodevice = '%s/counter0' % tacodev,
                  type = 'monitor',
                 ),
    #~ qm_ctr2 = device('devices.vendor.qmesydaq.Counter',
                     #~ description = 'QMesyDAQ Counter2',
                     #~ tacodevice = '%s/counter2' % tacodev,
                     #~ type = 'monitor',
                    #~ ),
    #~ qm_ctr3= device('devices.vendor.qmesydaq.Counter',
                    #~ description = 'QMesyDAQ Counter3',
                    #~ tacodevice = '%s/counter3' % tacodev,
                    #~ type = 'monitor',
                   #~ ),
    #~ qm_ev  = device('devices.vendor.qmesydaq.Counter',
                    #~ description = 'QMesyDAQ Events channel',
                    #~ tacodevice = '%s/events' % tacodev,
                    #~ type = 'counter',
                   #~ ),
    timer = device('devices.vendor.qmesydaq.Timer',
                   description = 'QMesyDAQ Timer',
                   tacodevice = '%s/timer' % tacodev,
                  ),
    image = device('devices.vendor.qmesydaq.Image',
                   description = 'QMesyDAQ Image',
                   tacodevice = '%s/det' % tacodev,
                  ),
    det   = device('devices.generic.Detector',
                   description = 'QMesyDAQ Image type Detector1',
                   timers = ['timer'],
                   counters = [],
                   monitors = ['mon1', 'mon2'],
                   images = ['image'],
                   fileformats = ['BerSANSFileSaver'],
                   subdir = 'bersans',
                  ),
)

startupcode = """
SetDetectors(det)
"""
