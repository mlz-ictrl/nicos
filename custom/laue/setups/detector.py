description = 'PSL 2-D detector'
group = 'lowlevel'

modules = ['nicos.laue.psldrv', 'nicos.laue.psldetector']
devices = dict(
    det1 = device('laue.psldetector.PSLDetector',
                 description = "PSL detector",
                 address = 'lauedet.laue.frm2',
                 port = 50000,
                 subdir='',
                 fileformats = ['raw','fits',],
                 lowlevel = False),
    raw = device('devices.fileformats.raw.RAWFileFormat'),
    fits = device('devices.fileformats.fits.FITSFileFormat'),
    )
