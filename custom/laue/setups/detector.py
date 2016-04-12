description = 'PSL 2-D detector'
group = 'lowlevel'

sysconfig = dict(
    datasinks = ['conssink', 'filesink', 'dmnsink',
                 'live', 'raw', 'sraw', 'tiff', 'hbin'],
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
               description = 'raw sink'),
    sraw=device('devices.datasinks.SingleRawImageSink',
                description = 'single raw sink',
                filenametemplate=['s%(pointcounter)08d.raw']),
    tiff=device('laue.lauetiff.TIFFLaueFileFormat',
                description = 'tiff sink',
                filenametemplate=['%(pointcounter)08d.tif']),
    hbin=device('laue.lauehbin.HBINLaueFileFormat',
                description = 'hbin sink',
                filenametemplate=['%(pointcounter)08d.hbin']),
    timer=device('devices.generic.VirtualTimer',
                 description = 'timer',
                 lowlevel=True),
    det1=device('devices.generic.detector.Detector',
                description = 'PSL detector',
                timers = ['timer'],
                images = ['image']),
)
