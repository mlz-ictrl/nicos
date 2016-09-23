description = 'Neutron camera'
group = 'optional'

tango_base = 'tango://phys.poli.frm2:10000/poli/'

sysconfig = dict(
    datasinks = ['tifformat'],
)

devices = dict(
    camtimer  = device('devices.tango.TimerChannel',
                       description = 'Timer for the neutron camera',
                       tangodevice = tango_base + 'atikccd/timer',
                      ),
    camimage  = device('frm2.camera.CameraImage',
                       description = 'Image for the neutron camera',
                       tangodevice = tango_base + 'atikccd/image',
                      ),
    cam       = device('devices.generic.Detector',
                       description = 'NeutronOptics camera',
                       timers = ['camtimer'],
                       monitors = [],
                       counters = [],
                       images = ['camimage'],
                      ),
    cam_temp  = device('devices.tango.AnalogOutput',
                       description = 'Temperature of neutron camera',
                       tangodevice = tango_base + 'atikccd/cooling',
                      ),
    tifformat = device('devices.datasinks.TIFFImageSink',
                       description = 'saves image data in TIFF format',
                       filenametemplate = ['%(proposal)s_%(pointcounter)08d.tiff'],
                       mode = 'I',
                      ),
)
