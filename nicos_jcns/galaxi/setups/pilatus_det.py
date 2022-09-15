# -*- coding: utf-8 -*-

description = 'GALAXI PILATUS2 R 1M detector setup'

group = 'optional'

display_order = 10

includes = ['absorber', 'jcns_io', 'jcns_mot', 'pindiodes']

tango_base = 'tango://phys.galaxi.jcns.fz-juelich.de:10000/galaxi/'

sysconfig = dict(datasinks = ['pilatus_filesink'])

# default photon and threshold energy
energy = dict(photon = 9.243, threshold = 8.0)

devices = dict(
    pilatus_config = device('nicos_jcns.devices.dectris.ConfigurationChannel',
        description = 'Configuration channel of the DECTRIS PILATUS2 R 1M '
        'detector.',
        tangodevice = tango_base + 'pilatus_det/configuration',
    ),
    pilatus_image = device('nicos.devices.entangle.ImageChannel',
        description = 'Image channel of the DECTRIS PILATUS2 R 1M detector.',
        tangodevice = tango_base + 'pilatus_det/image_channel',
    ),
    pilatus_timer = device('nicos.devices.entangle.TimerChannel',
        description = 'Timer channel of the DECTRIS PILATUS2 R 1M detector.',
        tangodevice = tango_base + 'pilatus_det/timer_channel',
    ),
    pilatus = device('nicos_jcns.devices.dectris.PILATUSDetector',
        description = 'DECTRIS PILATUS2 R 1M detector at the GALAXI '
        'diffractometer.',
        mxsettings = {'energy_range': (9.2247, 9.2517), 'wavelength': 1.341},
        detector_distance = 'detdistance',
        detector_voffset = 'detz',
        flux = 'ionichamber2',
        filter_transmission = 'absorber',
        chi = 'pchi',
        omega = 'pom',
        images = ['pilatus_image'],
        timers = ['pilatus_timer'],
        others = ['pilatus_config'],
    ),
    pilatus_filesink = device('nicos_jcns.devices.dectris.FileSink',
        description = 'Sets the path for the next image created by the '
        'PILATUS file writer.',
        detectors = ['pilatus'],
        filenametemplate = [
            '%(session.experiment.users)s_'
            '%(session.experiment.sample.filename)s_'
            '%(scancounter)s.%(pointnumber)s.tif',
        ],
    ),
)

startupcode = '''
AddDetector(pilatus)
pilatus.setEnergy(photon={photon:f}, threshold={threshold:f})
'''.format(**energy)
