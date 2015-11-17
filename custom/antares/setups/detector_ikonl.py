# -*- coding: utf-8 -*-

description = 'Andor IKON-L CCD camera'

group = 'optional'

includes = ['shutters', 'filesavers']

tango_host = 'tango://antareshw.antares.frm2:10000'

devices = dict(
    ikonl = device('antares.detector.AntaresIkonLCCD',
                 description = 'The Andor Ikon L CCD camera detector',
                 tangodevice = '%s/antares/detector/limaccd' % tango_host,
                 hwdevice = '%s/antares/detector/ikonl' % tango_host,
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
    ikonlTemp = device('devices.vendor.lima.Andor2TemperatureController',
                     description = 'The CCD chip temperature',
                     tangodevice = '%s/antares/detector/ikonl' % tango_host,
                     maxage = 5,
                     abslimits = (-100, 0),
                     userlimits = (-100, 0),
                     unit = 'degC',
                     precision = 3,
                     fmtstr = '%.0f',
                    ),
)

startupcode = '''
SetDetectors(ikonl)

## override hw setting to known good values.
ikonl.rotation = 90
ikonl.shutteropentime = 0.05
ikonl.shutterclosetime = 0.05
ikonl.shuttermode = 'auto'
ikonl.vsspeed = 38.55
ikonl.hsspeed = 1
ikonl.pgain = 1
'''
