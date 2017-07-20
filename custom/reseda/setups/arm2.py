#  -*- coding: utf-8 -*-

description = 'Arm 2 (MIEZE)'
group = 'optional'

taco_base = '//resedasrv.reseda.frm2/reseda'
tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    arm2_fg_frequency = device('nicos.devices.tango.AnalogOutput',
        description = 'Frequency Generator Arm 2 (Frequency)',
        tangodevice = '%s/arm2/fg_frequency' % tango_base,
    ),
    arm2_fg_amplitude = device('nicos.devices.tango.AnalogOutput',
        description = 'Frequency Generator Arm 2 (Amplitude)',
        tangodevice = '%s/arm2/fg_amplitude' % tango_base,
    ),
    arm2_fg_burst = device('nicos.devices.tango.DigitalOutput',
        description = 'Frequency Generator Arm 2 (Burst)',
        tangodevice = '%s/arm2/fg_burst' % tango_base,
    ),
    arm2_rot_mot = device('nicos.devices.tango.Motor',
        description = 'Rotation arm 2 (motor)',
        tangodevice = '%s/arm2/2theta' % tango_base,
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    arm2_rot_enc = device('nicos.devices.taco.Coder',
        description = 'Rotation arm 2 (encoder)',
        tacodevice = '%s/enc/arm2' % taco_base, # not enc/arm2 due to broken hw
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    arm2_rot_air = device('nicos.devices.tango.DigitalOutput',
        description = 'Rotation arm 1 (air)',
        tangodevice = '%s/iobox/plc_air_a2' % tango_base,
        fmtstr = '%.3f',
        lowlevel=True,
    ),
    arm2_rot = device('mira.axis.HoveringAxis',
        description = 'Rotation arm 1',
        motor = 'arm2_rot_mot',
        coder = 'arm2_rot_enc',
        switch = 'arm2_rot_air',
        startdelay = 2.0,
        stopdelay = 2.0,
        fmtstr = '%.3f',
        precision = 0.01,
    ),
)
