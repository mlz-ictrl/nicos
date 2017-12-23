#  -*- coding: utf-8 -*-

description = 'Arm 2 (MIEZE)'
group = 'optional'

taco_base = '//resedasrv.reseda.frm2/reseda'
tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    arm2_rot_mot = device('nicos.devices.tango.Motor',
        description = 'Rotation arm 2 (motor)',
        tangodevice = '%s/arm2/2theta' % tango_base,
        fmtstr = '%.3f',
        lowlevel = True,
        # abslimits = (-5.0, 60.0)
    ),
    arm2_rot_enc = device('nicos.devices.taco.Coder',
        description = 'Rotation arm 2 (encoder)',
        tacodevice = '%s/enc/arm2' % taco_base, # not enc/arm2 due to broken hw
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    arm2_rot_air = device('nicos.devices.tango.DigitalOutput',
        description = 'Rotation arm 2 (air)',
        tangodevice = '%s/iobox/plc_air_a2' % tango_base,
        fmtstr = '%.3f',
        lowlevel=True,
    ),
    arm2_rot = device('nicos_mlz.mira.devices.axis.HoveringAxis',
        description = 'Rotation arm 2',
        motor = 'arm2_rot_mot',
        coder = 'arm2_rot_enc',
        switch = 'arm2_rot_air',
        startdelay = 2.0,
        stopdelay = 2.0,
        fmtstr = '%.3f',
        precision = 0.01,
        # abslimits = (-5.0, 60.0),
    ),
)
