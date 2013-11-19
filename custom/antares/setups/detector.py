# -*- coding: utf-8 -*-

description = 'Andor DV936 CCD camera'

group = 'optional'

includes = ['shutters']

devices = dict(
    ccd = device('nicos.antares.detector.LimaCCD',
                 tangodevice = 'antares/detector/limaccd',
                 hwdevice = 'antares/detector/ikonl',
                 fastshutter = 'fastshutter',
                 maxage=10,
                 subdir='.',
                 flip=(False, True),
                 rotation=90,
                 shutteropentime=0.05,
                 shutterclosetime=0.05,
                 shuttermode='auto',
                 nametemplate='%08d.fits',
                 filecounter='/data/FRM-II/imagecounter',
                 vsspeed=38.55,
                 hsspeed=1,
                 pgain=1,
                ),
    ccdTemp = device('nicos.antares.detector.AndorTemperature',
                 tangodevice = 'antares/detector/ikonl',
                 maxage=5,
                 abslimits=(-100, 0),
                 userlimits=(-100, 0),
                 unit='degC',
                 precision=1,
                 fmtstr='%.0f',
                ),
)

startupcode = '''
SetDetectors(ccd)

ccd.rotation = 90
ccd.shutteropentime = 0.05
ccd.shutterclosetime = 0.05
ccd.shuttermode = 'auto'
ccd.vsspeed = 38.55
ccd.hsspeed = 1
ccd.pgain = 1
'''
