# -*- coding: utf-8 -*-

description = 'GALAXI MYTHEN R 1K detector setup'

group = 'optional'

display_order = 12

tango_base = 'tango://phys.galaxi.jcns.fz-juelich.de:10000/galaxi/mythen_det/'

sysconfig = dict(datasinks = ['mythen_imagesink'])

# default photon and threshold energy
energy = dict(photon = 9.243, threshold = 8.0)

devices = dict(
    mythen_config = device('nicos_jcns.devices.dectris.ConfigurationChannel',
        description = 'Configuration channel of the DECTRIS MYTHEN R 1K '
        'detector.',
        tangodevice = tango_base + 'configuration_channel',
    ),
    mythen_image = device('nicos.devices.entangle.ImageChannel',
        description = 'Image channel of the DECTRIS MYTHEN R 1K detector.',
        tangodevice = tango_base + 'image_channel',
    ),
    mythen_timer = device('nicos.devices.entangle.TimerChannel',
        description = 'Image channel of the DECTRIS MYTHEN R 1K detector.',
        tangodevice = tango_base + 'timer_channel',
    ),
    mythen = device('nicos_jcns.devices.dectris.MYTHENDetector',
        description = 'DECTRIS MYTHEN R 1K detector at the GALAXI '
        'diffractometer.',
        images = ['mythen_image'],
        timers = ['mythen_timer'],
        others = ['mythen_config'],
    ),
    mythen_imagesink = device('nicos_jcns.devices.dectris.MYTHENImageSink',
        description = 'Saves image data of the MYTHEN detector in a text '
        'file.',
        filenametemplate = [
            '%(Exp.users)s_%(session.experiment.sample.filename)s_'
            '%(scancounter)s.%(pointnumber)s.mythen'
        ],
        detectors = ['mythen'],
    ),
)

startupcode = '''
AddDetector(mythen)
mythen.setEnergy(photon={photon:f}, threshold={threshold:f})
'''.format(**energy)
