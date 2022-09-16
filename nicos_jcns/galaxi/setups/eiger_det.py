# -*- coding: utf-8 -*-

description = 'GALAXI EIGER2 R 4M detector setup'

group = 'optional'

display_order = 11

tango_base = 'tango://phys.galaxi.jcns.fz-juelich.de:10000/galaxi/eiger_det/'

sysconfig = dict(datasinks=['eiger_hdf5sink', 'eiger_tiffsink'])

# default photon and threshold energy
energy = dict(photon = 9.243, threshold = [8.0, 10.0])

devices = dict(
    eiger_config = device('nicos_jcns.devices.dectris.ConfigurationChannel',
        description = 'Configuration channel of the DECTRIS EIGER2 R 4M '
        'detector.',
        tangodevice = tango_base + 'configuration_channel',
    ),
    eiger_image = device('nicos.devices.entangle.ImageChannel',
        description = 'Image channel of the DECTRIS EIGER2 R 4M detector.',
        tangodevice = tango_base + 'image_channel',
    ),
    eiger_timer = device('nicos.devices.entangle.TimerChannel',
        description = 'Timer channel of the DECTRIS EIGER2 R 4M detector.',
        tangodevice = tango_base + 'timer_channel',
    ),
    eiger = device('nicos_jcns.devices.dectris.EIGERDetector',
        description = 'DECTRIS EIGER2 R 4M detector at the GALAXI '
        'diffractometer.',
        images = ['eiger_image'],
        timers = ['eiger_timer'],
        others = ['eiger_config'],
    ),
    eiger_hdf5sink = device('nicos_jcns.devices.dectris.FileSink',
        description = 'Sets the path for the next HDF5 image created by the '
        'EIGER file writer.',
        detectors = ['eiger'],
        filenametemplate = [
            '%(session.experiment.users)s_'
            '%(session.experiment.sample.filename)s_'
            '%(scancounter)s.%(pointnumber)s_master.h5',
        ],
    ),
    eiger_tiffsink = device('nicos.devices.datasinks.tiff.TIFFImageSink',
        description = 'Saves EIGER image data in TIFF format.',
        detectors = ['eiger'],
        filenametemplate = [
            '%(session.experiment.users)s_'
            '%(session.experiment.sample.filename)s_'
            '%(scancounter)s.%(pointnumber)s.tif',
        ],
        mode = 'I',
    ),
)

startupcode = '''
AddDetector(eiger)
eiger.setEnergy(photon={photon:f}, threshold={threshold})
'''.format(**energy)
