description = 'PSL 2-D detector'
group = 'lowlevel'

modules = ['nicos.laue.psldrv', 'nicos.laue.psldetector']
devices = dict(
    det1 = device('laue.psldetector.PSLDetector',
                 description = "PSL detector",
                 address = 'lauedet.laue.frm2',
                 port = 50000,
                 subdir='',
                 fileformats=['raw', 'fits', 'tiff', 'hbin'],
                 lowlevel = False),
    raw = device('devices.fileformats.raw.RAWFileFormat'),
    fits = device('devices.fileformats.fits.FITSFileFormat'),
    tiff = device('laue.lauetiff.TIFFLaueFileFormat',
                  filenametemplate=['%08d.tif']),
    hbin=device('laue.lauehbin.HBINLaueFileFormat',
                  filenametemplate=['%08d.hbin']),
    )
