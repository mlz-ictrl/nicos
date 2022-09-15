# -*- coding: utf-8 -*-

description = 'GALAXI EIGER2 R 4M detector setup'

group = 'optional'

display_order = 11

tango_base = 'tango://phys.galaxi.jcns.fz-juelich.de:10000/galaxi/'

sysconfig = dict(datasinks=['eiger_filesink'])

# default photon and threshold energy
energy = dict(photon = 9.243, threshold = [8.0, 10.0])

devices = dict(
    eiger_config = device('nicos_jcns.devices.dectris.ConfigurationChannel',
        description = 'Configuration channel of the DECTRIS EIGER2 R 4M '
        'detector.',
        tangodevice = tango_base + 'eiger_det/configuration',
    ),
    eiger_image = device('nicos.devices.entangle.ImageChannel',
        description = 'Image channel of the DECTRIS EIGER2 R 4M detector.',
        tangodevice = tango_base + 'eiger_det/image_channel',
    ),
    eiger_timer = device('nicos.devices.entangle.TimerChannel',
        description = 'Timer channel of the DECTRIS EIGER2 R 4M detector.',
        tangodevice = tango_base + 'eiger_det/timer_channel',
    ),
    eiger = device('nicos_jcns.devices.dectris.EIGERDetector',
        description = 'DECTRIS EIGER2 R 4M detector at the GALAXI '
        'diffractometer.',
        images = ['eiger_image'],
        timers = ['eiger_timer'],
        others = ['eiger_config'],
    ),
    eiger_filesink = device('nicos_jcns.devices.dectris.FileSink',
        detectors = ['eiger'],
        description = 'Sets the path for the next image created by the '
        'EIGER file writer.',
        filenametemplate = [
            '%(session.experiment.users)s_'
            '%(session.experiment.sample.filename)s_'
            '%(scancounter)s.%(pointnumber)s_master.h5',
        ],
    ),
)

startupcode = '''
AddDetector(eiger)
eiger.setEnergy(photon={photon:f}, threshold={threshold})
'''.format(**energy)
