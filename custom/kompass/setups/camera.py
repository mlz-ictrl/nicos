description = 'neutron camera'
group = 'optional'

tango_base = 'tango://kompasshw.kompass.frm2:10000/kompass/'

sysconfig = dict(
    datasinks = ['tifformat'],
)

devices = dict(
    camtimer = device('devices.tango.TimerChannel',
                      description = 'timer for the Neutron camera',
                      tangodevice = tango_base + 'camera/timer',
                     ),
    camimage = device('frm2.camera.CameraImage',
                      description = 'image for the Neutron camera',
                      tangodevice = tango_base + 'camera/image',
                     ),

    cam      = device('devices.generic.Detector',
                      description = 'NeutronOptics camera',
                      timers = ['camtimer'],
                      monitors = [],
                      counters = [],
                      images = ['camimage'],
                     ),
    tifformat = device("devices.datasinks.TIFFImageSink",
                       description = "Saves image data in TIFF format",
                       filenametemplate = ["%(proposal)s_%(pointcounter)08d.tiff"],
                       mode = "I",
                      ),
)
