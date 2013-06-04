# -*- coding: utf-8 -*-

description = 'Andor DV936 CCD camera'
group = 'optional'

includes = []

devices = dict(
    ccd = device('nicos.antares.detector.LimaCCD',
                  description = 'CCD Camera',
                  tangodevice = 'antares/detector/limaccd',
                  hwdevice = 'antares/detector/ikonl',
                  subdir='.',
#                  subdir='test',
#                  datapath=['/data/FRM-II/'],
                  nametemplate='%08d.fits',
                ),
    ccdTemp = device('nicos.antares.detector.AndorTemperature',
                      description = 'Temperature of CCD-chip',
                      tangodevice = 'antares/detector/ikonl',
                      maxage=12,
                      pollinterval = 5,
                      abslimits=(-80,0),
                      userlimits=(-80,0),
                      unit='C',
                      precision=1,
                    ),
)

startupcode = '''
'''
