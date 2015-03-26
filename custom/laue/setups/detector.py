description = 'PSL 2-D detector'
group = 'lowlevel'

modules = ['nicos.laue.psldrv', 'nicos.laue.psldetector']
devices = dict(
    det1 = device('laue.psldetector.PSLDetector',
                 description = "PSL detector",
                 address = 'lauedet.laue.frm2',
                 port = 50000,
                 subdir='',
                 fileformats=['live', 'tiff', 'hbin', 'raw','sraw'],
                 lowlevel = False),
    live=device('devices.fileformats.liveview.LiveViewSink'),
    raw=device('devices.fileformats.raw.RAWFileFormat'),
    sraw=device('devices.fileformats.raw.SingleRAWFileFormat',
                filenametemplate=['s%08d.raw']),
    tiff=device('laue.lauetiff.TIFFLaueFileFormat',
                filenametemplate=['%08d.tif']),
    hbin=device('laue.lauehbin.HBINLaueFileFormat',
                filenametemplate=['%08d.hbin']),
)
