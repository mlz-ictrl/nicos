# -*- coding: utf-8 -*-

description = 'Detector file savers'

group = 'lowlevel'

devices = dict(
    FITSFileSaver = device('devices.fileformats.fits.FITSFileFormat',
                           description = 'Saves image data in FITS format',
                           filenametemplate = ['%08d.fits'],
                          ),
)

startupcode = '''
'''
