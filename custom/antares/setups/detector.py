# -*- coding: utf-8 -*-

description = 'Andor DV936 CCD camera'

group = 'optional'

includes = ['shutters']

devices = dict(
    ccd = device('nicos.antares.detector.LimaCCD',
                tangodevice = 'antares/detector/limaccd',
                hwdevice = 'antares/detector/ikonl',
                fastshutter = 'fastshutter',
                maxage=5,
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
                abslimits=(-80,0),
                userlimits=(-80,0),
                unit='degC',
                precision=1,
                ),
)

startupcode = '''
SetDetectors(ccd)
'''
