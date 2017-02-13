#  -*- coding: utf-8 -*-

description = 'Arm 2 (MIEZE)'
group = 'optional'

taco_base = '//resedasrv.reseda.frm2/reseda'
tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    arm2_rot_mot = device('devices.taco.Motor',
        description = 'Rotation arm 2 (motor)',
        tacodevice = '%s/husco1/motor2' % taco_base,
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    arm2_rot_enc = device('devices.taco.Coder',
        description = 'Rotation arm 2 (encoder)',
        tacodevice = '%s/enc/arm2' % taco_base, # not enc/arm1 due to broken hw
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    arm2_rot_air = device('devices.tango.DigitalOutput',
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
        precision = 0.1,
    ),
)
