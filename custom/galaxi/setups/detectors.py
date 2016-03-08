# -*- coding: utf-8 -*-

description = 'GALAXI Mythen and Pilatus detector setup'

group = 'optional'

includes = ['absorber', 'jcns_mot', 'pindiodes', 'jcns_io']

tango_base = 'tango://localhost:10000/galaxi/'

devices = dict(
    GALAXIFileSaver = device('galaxi.galaxifileformat.GALAXIFileFormat',
                             lowlevel = True,
                             filenametemplate = ['%(Exp.users)s'
                                                 '_%(session.experiment.sample.'
                                                 'samplename)s_ '
                                                 '%(session.experiment.'
                                                 'lastscan)s_%(scanpoint)s'
                                                 '.mydat'],
                            ),
    mythen          = device('galaxi.mythen.MythenDetector',
                             description = 'GALAXI Mythen detector',
                             fileformats = ['GALAXIFileSaver'],
                             fmtstr = '%s',
                             subdir = '.',
                             tangodevice = tango_base + 'mythen/1',
                            ),
    pilatus         = device('galaxi.pilatus.PilatusDetector',
                             description = 'GALAXI Pilatus detector',
                             fmtstr = '%s',
                             subdir = '',
                             tangodevice = tango_base + 'pilatus/1',
                             pathorigin = '/disk2/images/',
                             energyrange = [9224.7, 9251.7],
                             energy = 9.243,
                             threshold = 7.0,
                             wavelength = 1.341,
                             detdistance = 'detdistance',
                             detz = 'detz',
                             ionichamber2 = 'ionichamber2',
                             absorber = 'absorber',
                             pchi = 'pchi',
                             pom = 'pom'
                            ),
)

startupcode = '''
SetDetectors(pilatus)
'''
