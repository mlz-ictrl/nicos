#  -*- coding: utf-8 -*-

description = '3He detector'
group = 'optional'
includes = ['det_base', 'coderbus']
excludes = ['det_cascade']

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    scandet = device('nicos_mlz.reseda.devices.scandet.ScanningDetector',
        description = 'Scanning detector for scans per echotime',
        scandev = 'nse1',
        detector = 'det',
        maxage = 2,
        pollinterval = 0.5,
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'FRM II multichannel counter card',
        timers = ['timer'],
        monitors = ['monitor1', ],
        counters = ['counter'],
        fmtstr = 'timer %s, monitor1 %s, ctr %s',
        maxage = 2,
        pollinterval = 0.5,
    ),
    det_hv = device('nicos.devices.entangle.PowerSupply',
        description = 'High voltage power supply of the 3he detector',
        tangodevice = '%s/3he_det/hv' % tango_base,
        abslimits = (0, 1350),
        unit = 'V',
    ),
    det_rot_mot = device('nicos.devices.entangle.Motor',
        description = 'Detector rotation (motor)',
        tangodevice = '%s/3he_det/rot' % tango_base,
        fmtstr = '%.3f',
        lowlevel = True,
        unit = 'deg',
    ),
    det_rot_enc = device('nicos.devices.vendor.ipc.Coder',
        description = 'Detector rotation (encoder)',
        # bitlength: 25
        # direction: forward
        # encoding: gray
        # offset: -143.223950e+02
        # parity: no
        # protocol: ssi
        # stepsperunit:
        # type: EncoderEncoder
        bus = 'encoderbus',
        addr = 83,
        slope = 163840.,
        zerosteps = 23465812,
        circular = 360,
        confbyte = 0x79, # 0111 1001
        unit = 'deg',
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    det_rot = device('nicos.devices.generic.Axis',
        description = 'Detector rotation',
        motor = 'det_rot_mot',
        coder = 'det_rot_enc',
        fmtstr = '%.3f',
        precision = 0.1,
        unit = 'deg',
    ),
    det_x = device('nicos.devices.entangle.Motor',
        description = 'Detector x translation (motor)',
        tangodevice = '%s/3he_det/x' % tango_base,
        fmtstr = '%.1f',
        unit = 'mm',
    ),
    det_y = device('nicos.devices.entangle.Motor',
        description = 'Detector y translation (motor)',
        tangodevice = '%s/3he_det/y' % tango_base,
        fmtstr = '%.1f',
        unit = 'mm'
    ),
)

startupcode = '''
SetDetectors(det)
'''
