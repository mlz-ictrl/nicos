#  -*- coding: utf-8 -*-

description = 'Sample table (translation)'
group = 'optional'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

includes = ['coderbus']

devices = dict(
    srz_mot = device('nicos.devices.tango.Motor',
        description = 'Sample rotation: z (motor)',
        tangodevice = '%s/sampletable/srz' % tango_base,
        fmtstr = '%.3f',
        unit = 'deg',
        lowlevel = True,
    ),
    srz_enc = device('nicos.devices.vendor.ipc.Coder',
        description = 'Sample rotation: z (encoder)',
        # bitlength: 25l
        # busaddr: 88l
        # devname: reseda/rs485/encoder
        # encoding: gray
        # offset: 3977.53247
        # parity: no
        # protocol: ssi
        # stepsperunit: 8192.0
        # type: EncoderEncoder
        bus = 'encoderbus',
        addr = 88,
        slope = 8192.,
        zerosteps = 32583949,
        circular = 360,
        confbyte = 0x79, # 0111 1001
        fmtstr = '%.3f',
        unit = 'deg',
        lowlevel = True,
    ),
    srz = device('nicos.devices.generic.Axis',
        description = 'Sample rotation: z',
        motor = 'srz_mot',
        coder = 'srz_enc',
        fmtstr = '%.3f',
        precision = 0.05,
        unit = 'deg',
    ),
    stx = device('nicos.devices.tango.Motor',
        description = 'Sample table: x',
        tangodevice = '%s/sampletable/stx' % tango_base,
        fmtstr = '%.2f',
        unit = 'mm',
    ),
    sty = device('nicos.devices.tango.Motor',
        description = 'Sample table: y',
        tangodevice = '%s/sampletable/sty' % tango_base,
        fmtstr = '%.2f',
        unit = 'mm'
    ),
    sgx = device('nicos.devices.tango.Motor',
        description = 'Sample goniometer: x',
        tangodevice = '%s/sampletable/sgx' % tango_base,
        fmtstr = '%.3f',
        unit = 'deg',
    ),
    sgy = device('nicos.devices.tango.Motor',
        description = 'Sample goniometer: x',
        tangodevice = '%s/sampletable/sgy' % tango_base,
        fmtstr = '%.3f',
        unit = 'deg',
    ),
    st_air = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Sample table pressured air',
        tangodevice = '%s/iobox/plc_air_sampletable' % tango_base,
        mapping = {'on': 1,
                   'off': 0},
        unit = '',
    ),
)
