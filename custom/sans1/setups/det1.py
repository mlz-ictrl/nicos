description = 'qmesydaq devices for SANS1'

# included by sans1
group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

sysconfig = dict(
    datasinks = ['BerSANSFileSaver'],
)

devices = dict(
    BerSANSFileSaver  = device('sans1.bersans.BerSANSImageSink',
                               description = 'Saves image data in BerSANS format',
                               filenametemplate = ['D%(pointcounter)07d.001',
                                                   '/data_user/D%(pointcounter)07d.001'],
                               flipimage = 'updown',
                               lowlevel = True,
                               subdir = 'bersans',
                              ),
    #~ LiveViewSink = device('devices.datasinks.LiveViewSink',
                               #~ description = 'Sends image data to LiveViewWidget',
                               #~ filenametemplate=[],
                               #~ lowlevel = True,
                              #~ ),
    LivePNGSinkLog   = device('devices.datasinks.PNGLiveFileSink',
                              description = 'Saves live image as .png every now and then',
                              filename = '/sans1control/webroot/live_log.png',
                              log10 = True,
                              interval = 15,
                              lowlevel = True,
                             ),
    LivePNGSink      = device('devices.datasinks.PNGLiveFileSink',
                              description = 'Saves live image as .png every now and then',
                              filename = '/sans1control/webroot/live_lin.png',
                              log10 = False,
                              interval = 15,
                              lowlevel = True,
                             ),

    det1_mon1 = device('devices.vendor.qmesydaq.taco.Counter',
                       description = 'QMesyDAQ Counter0',
                       tacodevice = '//%s/sans1/qmesydaq/counter0' % nethost,
                       type = 'monitor',
                      ),
    det1_mon2 = device('devices.vendor.qmesydaq.taco.Counter',
                       description = 'QMesyDAQ Counter1',
                       tacodevice = '//%s/sans1/qmesydaq/counter1' % nethost,
                       type = 'monitor',
                      ),
    det1_mon3 = device('devices.vendor.qmesydaq.taco.Counter',
                       description = 'QMesyDAQ Counter2',
                       tacodevice = '//%s/sans1/qmesydaq/counter2' % nethost,
                       type = 'monitor',
                      ),
    det1_mon4 = device('devices.vendor.qmesydaq.taco.Counter',
                       description = 'QMesyDAQ Counter3',
                       tacodevice = '//%s/sans1/qmesydaq/counter3' % nethost,
                       type = 'monitor',
                       lowlevel = 'True',
                      ),
    det1_ev  = device('devices.vendor.qmesydaq.taco.Counter',
                      description = 'QMesyDAQ Events channel',
                      tacodevice = '//%s/sans1/qmesydaq/events' % nethost,
                      type = 'counter',
                     ),
    det1_timer = device('devices.vendor.qmesydaq.taco.Timer',
                        description = 'QMesyDAQ Timer',
                        tacodevice = '//%s/sans1/qmesydaq/timer' % nethost,
                       ),
    det1_image = device('devices.vendor.qmesydaq.taco.Image',
                        description = 'QMesyDAQ Image',
                        tacodevice = '//%s/sans1/qmesydaq/det' % nethost,
                       ),
    det1    = device('devices.generic.Detector',
                     description = 'QMesyDAQ Image type Detector1',
                     timers = ['det1_timer'],
                     counters = [],
                     monitors = ['det1_mon1', 'det1_mon2', 'TISANE_det_pulses'],
                     images = ['det1_image'],
                    ),
    TISANE_det_pulses = device('devices.generic.DeviceAlias',
                           alias = 'det1_mon3',
                          )
)

startupcode = '''
SetDetectors(det1)
'''
