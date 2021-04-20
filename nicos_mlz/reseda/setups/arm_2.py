#  -*- coding: utf-8 -*-

description = 'Arm 2 (MIEZE)'
group = 'optional'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

includes = ['coderbus']

devices = dict(
    arm2_rot_mot = device('nicos.devices.entangle.Motor',
        description = 'Rotation arm 2 (motor)',
        tangodevice = '%s/arm2/2theta' % tango_base,
        fmtstr = '%.3f',
        lowlevel = True,
        # abslimits = (-5.0, 60.0)
    ),
    arm2_rot_enc = device('nicos.devices.vendor.ipc.Coder',
        description = 'Rotation arm 2 (encoder)',
        # bitlength: 25
        # busaddr: 87l
        # direction: forward
        # encoding: gray
        # offset: -78441.6815
        # parity: no
        # protocol: ssi
        # stepsperunit: 427.0
        # type: EncoderEncoder
        bus = 'encoderbus',
        addr = 87,
        slope = 427.,
        zerosteps = 33376131,
        circular = -360,
        confbyte = 0x79, # 0111 1001
        unit = 'deg',
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    arm2_rot_air = device('nicos.devices.entangle.DigitalOutput',
        description = 'Rotation arm 2 (air)',
        tangodevice = '%s/iobox/plc_air_a2' % tango_base,
        fmtstr = '%d',
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
        unit = 'deg'
        #pollinterval = 60,
        #maxage = 119,
    ),
)
