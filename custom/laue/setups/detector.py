description = 'PSL 2-D detector'
group = 'lowlevel'

sysconfig = dict(
    datasinks = ['tiff', 'raw', 'sraw', 'live' ],
)


modules = ['nicos.laue.psldrv', 'nicos.laue.psldetector']
devices = dict(
    image=device('laue.psldetector.PSLDetector',
                 description = 'PSL detector image',
                 address = 'lauedet.laue.frm2',
                 port = 50000),
    live=device('devices.datasinks.LiveViewSink',
                description = 'live sink'),
    raw=device('devices.datasinks.RawImageSink',
               description = 'raw sink',
               filenametemplate=['s%(pointcounter)08d.raw'],
               subdir=''),
    sraw=device('devices.datasinks.SingleRawImageSink',
                description = 'single raw sink',
                filenametemplate=['s%(pointcounter)08d.sraw'],
                subdir=''),
    tiff=device('laue.lauetiff.TIFFLaueSink',
                description = 'tiff sink',
                filenametemplate=['%(pointcounter)08d.tif'],
                subdir=''),
    timer=device('devices.generic.VirtualTimer',
                 description = 'timer',
                 lowlevel=True),
    det1=device('devices.generic.Detector',
                description = 'PSL detector',
                timers = ['timer'],
                images = ['image']),
)
