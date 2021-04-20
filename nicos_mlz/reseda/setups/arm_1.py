#  -*- coding: utf-8 -*-

description = 'Arm 1 (NRSE)'
group = 'optional'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

includes = ['coderbus']

devices = dict(
    arm1_rot_mot = device('nicos.devices.entangle.Motor',
        description = 'Rotation arm 1 (motor)',
        tangodevice = '%s/arm1/2theta' % tango_base,
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    arm1_rot_enc = device('nicos.devices.vendor.ipc.Coder',
        description = 'Rotation arm 1 (encoder)',
        # bitlength: 25
        # devname: reseda/rs485/encoder
        # direction: forward
        # encoding: gray
        # offset: -180.0
        # parity: no
        # protocol: ssi
        # stepsperunit: 427.0
        # type: EncoderEncoder
        bus = 'encoderbus',
        addr = 86,
        slope = 427.,
        zerosteps = 33506891,
        circular = -360,
        confbyte = 0x79, # 0111 1001
        unit = 'deg',
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    arm1_rot_air = device('nicos.devices.entangle.DigitalOutput',
        description = 'Rotation arm 1 (air)',
        tangodevice = '%s/iobox/plc_air_a1' % tango_base,
        fmtstr = '%d',
        lowlevel = True,
    ),
    arm1_rot = device('nicos_mlz.mira.devices.axis.HoveringAxis',
        description = 'Rotation arm 1',
        motor = 'arm1_rot_mot',
        coder = 'arm1_rot_enc',
        switch = 'arm1_rot_air',
        startdelay = 2.0,
        stopdelay = 2.0,
        fmtstr = '%.2f',
        precision = 0.05,
        pollinterval = 60,
        maxage = 119,
        unit = 'deg',
    ),
    T_arm1_coil1 = device('nicos.devices.entangle.AnalogInput',
        description = 'Arm 1 coil 1 temperature',
        tangodevice = '%s/iobox/plc_t_arm1coil1' % tango_base,
        fmtstr = '%.1f',
        pollinterval = 10,
        maxage = 21,
        unit = 'degC',
    ),
    T_arm1_coil2 = device('nicos.devices.entangle.AnalogInput',
        description = 'Arm 1 coil 2 temperature',
        tangodevice = '%s/iobox/plc_t_arm1coil2' % tango_base,
        fmtstr = '%.1f',
        pollinterval = 10,
        maxage = 21,
        unit = 'degC',
    ),
    T_arm1_coil3 = device('nicos.devices.entangle.AnalogInput',
        description = 'Arm 1 coil 3 temperature',
        tangodevice = '%s/iobox/plc_t_arm1coil3' % tango_base,
        fmtstr = '%.1f',
        pollinterval = 10,
        maxage = 21,
        unit = 'degC',
    ),
    T_arm1_coil4 = device('nicos.devices.entangle.AnalogInput',
        description = 'Arm 1 coil 4 temperature',
        tangodevice = '%s/iobox/plc_t_arm1coil4' % tango_base,
        fmtstr = '%.1f',
        pollinterval = 10,
        maxage = 21,
        unit = 'degC',
    ),
)
