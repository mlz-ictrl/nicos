#  -*- coding: utf-8 -*-

description = 'Arm 0 (NRSE)'
group = 'optional'

taco_base = '//resedasrv.reseda.frm2/reseda'
tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    arm0_fg_frequency = device('nicos.devices.tango.AnalogOutput',
        description = 'Frequency Generator Arm 0 (Frequency)',
        tangodevice = '%s/arm0/fg_frequency' % tango_base,
    ),
    arm0_fg_amplitude = device('nicos.devices.tango.AnalogOutput',
        description = 'Frequency Generator Arm 0 (Amplitude)',
        tangodevice = '%s/arm0/fg_amplitude' % tango_base,
    ),
    arm0_fg_burst = device('nicos.devices.tango.DigitalOutput',
        description = 'Frequency Generator Arm 0 (Burst)',
        tangodevice = '%s/arm0/fg_burst' % tango_base,
    ),
)
