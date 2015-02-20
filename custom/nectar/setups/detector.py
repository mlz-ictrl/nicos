# -*- coding: utf-8 -*-

description = 'Andor DV434 CCD camera'

group = 'optional'

tango_host = 'tango://nectarccd01.nectar.frm2:10000'

devices = dict(
    FITSFileSaver = device('devices.fileformats.fits.FITSFileFormat',
                           description = 'Saves image data in FITS format',
                           filenametemplate = ['%08d.fits'],
                          ),

    ccd = device('devices.vendor.lima.Andor2LimaCCD',
                 description = 'The CCD detector',
                 tangodevice = '%s/nectar/detector/limaccd' % tango_host,
                 hwdevice = '%s/nectar/detector/dv434' % tango_host,
                 pollinterval = 5,
                 maxage = 12,
                 flip = (False, False),
                 rotation = 0,
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
                     description = 'Temperature of the CCD detector',
                     tangodevice = '%s/nectar/detector/dv434' % tango_host,
                     pollinterval = 5,
                     maxage = 12,
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
ccd.rotation = 0
ccd.shutteropentime = 0.05
ccd.shutterclosetime = 0.05
ccd.shuttermode = 'auto'
ccd.vsspeed = 38.55
ccd.hsspeed = 1
ccd.pgain = 1
'''
