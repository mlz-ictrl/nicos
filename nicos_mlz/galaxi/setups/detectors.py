# -*- coding: utf-8 -*-

description = 'GALAXI Mythen and Pilatus detector setup'

group = 'optional'

includes = ['absorber', 'jcns_mot', 'pindiodes', 'jcns_io']

tango_base = 'tango://localhost:10000/galaxi/'

sysconfig = dict(
    datasinks = ['mythensink', 'pilatussink'],
)

devices = dict(
    mythen_timer    = device('nicos_mlz.galaxi.devices.mythen.MythenTimer',
                             description = 'Timer',
                             tangodevice = tango_base + 'Mythen/1',
                             lowlevel = True,
                            ),
    mythen_image    = device('nicos_mlz.galaxi.devices.mythen.MythenImage',
                             description = 'GALAXI Mythen detector data',
                             tangodevice = tango_base + 'Mythen/1',
                            ),
    mythen          = device('nicos_mlz.galaxi.devices.mythen.MythenDetector',
                             description = 'GALAXI Mythen detector',
                             timers = ['mythen_timer'],
                             images = ['mythen_image'],
                             monitors = [],
                            ),
    pilatus         = device('nicos_mlz.galaxi.devices.pilatus.PilatusDetector',
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
    pilatussink     = device('nicos_mlz.galaxi.devices.pilatus.PilatusSink',
                             detector = 'pilatus',
                             detectors = ['pilatus'],
                             lowlevel = True,
                            ),
    mythensink      = device('nicos_mlz.galaxi.devices.mythendatasink.MythenImageSink',
                             filenametemplate =
                              ['%(Exp.users)s_%(session.experiment.sample.'
                               'filename)s_%(scancounter)s_%(pointnumber)s'
                               '.mydat'],
                             lowlevel = True,
                             detectors = ['mythen']
                            ),

)

startupcode = '''
SetDetectors(pilatus)
'''
