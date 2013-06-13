# -*- coding: utf-8 -*-

description = 'Andor DV936 CCD camera'
group = 'optional'

includes = []

devices = dict(
    ccd = device('nicos.antares.detector.LimaCCD',
                description = 'CCD Camera',
                tangodevice = 'antares/detector/limaccd',
                hwdevice = 'antares/detector/ikonl',
                maxage=1,
                subdir='.',
                flip=(False, True),
                rotation=90,
                shutteropentime=0.05,
                shutterclosetime=0.05,
                shuttermode='auto',
                nametemplate='%08d.fits',
                ),
    ccdTemp = device('nicos.antares.detector.AndorTemperature',
                description = 'Temperature of CCD-chip',
                tangodevice = 'antares/detector/ikonl',
                maxage=1,
                abslimits=(-80,0),
                userlimits=(-80,0),
                unit='degC',
                precision=1,
                ),
)

startupcode = '''
SetDetectors(ccd)
'''
