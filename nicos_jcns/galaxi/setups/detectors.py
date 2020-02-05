# -*- coding: utf-8 -*-

description = 'GALAXI Mythen and Pilatus detector setup'

group = 'optional'

display_order = 10

includes = ['absorber', 'jcns_io', 'jcns_mot', 'pindiodes']

tango_base = 'tango://phys.galaxi.kfa-juelich.de:10000/galaxi/'

sysconfig = dict(datasinks = ['mythen_imagesink', 'pilatus_tiffsink'])

# default x-ray and threshold energy for all detectors
energy = dict(xray = 9.243, threshold = 8.0)

devices = dict(
    mythen_image = device('nicos_jcns.galaxi.devices.mythen_det.ImageChannel',
        description = 'Image channel of the DECTRIS Mythen detector.',
        tangodevice = tango_base + 'mythen_det/image_channel',
    ),
    mythen_timer = device('nicos.devices.tango.TimerChannel',
        description = 'Image channel of the DECTRIS Mythen detector.',
        tangodevice = tango_base + 'mythen_det/timer_channel',
    ),
    mythen = device('nicos.devices.generic.Detector',
        description = 'DECTRIS Mythen detector at the GALAXI diffractometer.',
        images = ['mythen_image'],
        timers = ['mythen_timer'],
    ),
    mythen_imagesink = device('nicos_jcns.galaxi.devices.mythen_det.ImageSink',
        filenametemplate = [
            '%(Exp.users)s_%(session.experiment.sample.filename)s_'
            '%(scancounter)s.%(pointnumber)s.mythen'
        ],
        detectors = ['mythen'],
    ),
    pilatus_config = device('nicos_jcns.devices.pilatus_det.Configuration',
        description = 'Configuration channel of the DECTRIS Pilatus 1M '
        'detector.',
        tangodevice = tango_base + 'pilatus_det/configuration',
        mxsettings = {
            'energy_range': (9.2247, 9.2517),
            'wavelength': 1.341,
        },
        detector_distance = 'detdistance',
        detector_voffset = 'detz',
        flux = 'ionichamber2',
        filter_transmission = 'absorber',
        chi = 'pchi',
        omega = 'pom',
    ),
    pilatus_tiffsink = device('nicos_jcns.devices.pilatus_det.TIFFImageSink',
        detectors = ['pilatus'],
        filenametemplate = [
            '%(session.experiment.users)s_'
            '%(session.experiment.sample.filename)s_'
            '%(scancounter)s.%(pointnumber)s.tif',
        ],
    ),
    pilatus_image = device('nicos.devices.tango.ImageChannel',
        description = 'Image channel of the DECTRIS Pilatus 1M detector.',
        tangodevice = tango_base + 'pilatus_det/image_channel',
    ),
    pilatus_timer = device('nicos.devices.tango.TimerChannel',
        description = 'Timer channel of the DECTRIS Pilatus 1M detector.',
        tangodevice = tango_base + 'pilatus_det/timer_channel',
    ),
    pilatus = device('nicos_jcns.devices.pilatus_det.Detector',
        description = 'DECTRIS Pilatus 1M detector at the GALAXI '
        'diffractometer.',
        images = ['pilatus_image'],
        timers = ['pilatus_timer'],
        others = ['pilatus_config'],
    ),
)

startupcode = '''
SetDetectorEnergy(xray={xray:f}, threshold={threshold:f}, wait=False)
SetDetectors(pilatus)
'''.format(**energy)
