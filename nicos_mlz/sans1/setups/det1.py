description = 'qmesydaq devices for SANS1'

# included by sans1
group = 'lowlevel'

tango_base = 'tango://mesydaq.sans1.frm2.tum.de:10000/qm/qmesydaq/'

sysconfig = dict(
    datasinks = ['BerSANSFileSaver', 'LivePNGSink', 'LivePNGSinkLog',
                 'DetectorSetup', 'DetectorCalibration'],
)

devices = dict(
    BerSANSFileSaver = device('nicos_mlz.sans1.devices.bersans.BerSANSImageSink',
        description = 'Saves image data in BerSANS format',
        filenametemplate = [
            'D%(pointcounter)07d.001', '/data_user/D%(pointcounter)07d.001'
        ],
        subdir = 'hist',
    ),
    # LiveViewSink = device('nicos.devices.datasinks.LiveViewSink',
    #     description = 'Sends image data to LiveViewWidget',
    #     filenametemplate=[],
    # ),
    LivePNGSinkLog = device('nicos.devices.datasinks.PNGLiveFileSink',
        description = 'Saves live image as .png every now and then',
        filename = '/control/webroot/live_log.png',
        log10 = True,
        interval = 15,
    ),
    LivePNGSink = device('nicos.devices.datasinks.PNGLiveFileSink',
        description = 'Saves live image as .png every now and then',
        filename = '/control/webroot/live_lin.png',
        log10 = False,
        interval = 15,
    ),
    Histogram = device('nicos_mlz.devices.qmesydaqsinks.HistogramSink',
        description = 'Histogram data written via QMesyDAQ',
        image = 'det1_image',
        subdir = 'mtxt',
        filenametemplate = ['%(pointcounter)07d.mtxt'],
    ),
    Listmode = device('nicos_mlz.devices.qmesydaqsinks.ListmodeSink',
        description = 'Listmode data written via QMesyDAQ',
        image = 'det1_image',
        subdir = 'list',
        filenametemplate = ['%(pointcounter)07d.mdat'],
    ),
    DetectorSetup = device('nicos_mlz.sans1.devices.copysink.CopySink',
        description = 'Save the current detector setup file',
        source = 'configfile',
        subdir = 'configs',
        path = '/data/qmesydaq/configs/configuration_2016_07_13',
        filenametemplate = ['config_%(pointcounter)07d.mcfg'],
    ),
    DetectorCalibration = device('nicos_mlz.sans1.devices.copysink.CopySink',
        description = 'Save the current detector calibration file',
        source = 'calibrationfile',
        subdir = 'configs',
        path = '/data/qmesydaq/configs/pos_calibration_2016_07_13',
        filenametemplate = ['calib_%(pointcounter)07d.txt'],
    ),
    det1_mon1 = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ Counter0',
        tangodevice = tango_base + 'counter0',
        type = 'monitor',
    ),
    det1_mon2 = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ Counter1',
        tangodevice = tango_base + 'counter1',
        type = 'monitor',
    ),
    det1_mon3 = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ Counter2 (reference for tisane)',
        tangodevice = tango_base + 'counter2',
        type = 'monitor',
    ),
    det1_ev = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ Events channel',
        tangodevice = tango_base + 'events',
        type = 'counter',
    ),
    det1_timer = device('nicos.devices.entangle.TimerChannel',
        description = 'QMesyDAQ Timer',
        tangodevice = tango_base + 'timer',
    ),
    det1_image = device('nicos.devices.vendor.qmesydaq.tango.ImageChannel',
        description = 'QMesyDAQ Image',
        tangodevice = tango_base + 'image',
        flipaxes = [0],  # flip image up-down
    ),
    # the combined detector device is in sans1.py or tisane.py
)

startupcode = '''
SetDetectors(det1)
'''
