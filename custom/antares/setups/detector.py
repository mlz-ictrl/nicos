# -*- coding: utf-8 -*-

description = 'Andor DV936 CCD camera'

group = 'optional'

includes = ['shutters']

tango_host = 'antareshw.antares.frm2:10000'

devices = dict(
    FITSFileSaver = device('devices.fileformats.fits.FITSFileFormat',
                 description = 'Saves image data in FITS format',
                 filenametemplate = ['%08d.fits'],
                 ),

    ccd = device('antares.ikonl.AntaresIkonLCCD',
                 tangodevice = 'tango://%s/antares/detector/limaccd' % tango_host,
                 hwdevice = 'tango://%s/antares/detector/ikonl' % tango_host,
                 fastshutter = 'fastshutter',
                 pollinterval = 3,
                 maxage = 9,
                 flip = (False, True),
                 rotation = 90,
                 shutteropentime = 0.05,
                 shutterclosetime = 0.05,
                 shuttermode = 'auto',
                 vsspeed = 38.55,
                 hsspeed = 1,
                 pgain = 1,
                 subdir = '.',
                 fileformats = ['FITSFileSaver'],
                ),
    ccdTemp = device('devices.vendor.lima.Andor2TemperatureController',
                 tangodevice = 'tango://%s/antares/detector/ikonl' % tango_host,
                 maxage = 5,
                 abslimits = (-100, 0),
                 userlimits = (-100, 0),
                 unit = 'degC',
                 precision = 3,
                 fmtstr = '%.0f',
                ),
)

startupcode = '''
SetDetectors(ccd)

## override hw setting to known good values.
ccd.rotation = 90
ccd.shutteropentime = 0.05
ccd.shutterclosetime = 0.05
ccd.shuttermode = 'auto'
ccd.vsspeed = 38.55
ccd.hsspeed = 1
ccd.pgain = 1
'''
