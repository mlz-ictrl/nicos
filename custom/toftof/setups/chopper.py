description = 'chopper setup'
includes = ['system']

devices = dict(
    ch           = device('nicos.toftof.chopper.Controller',
                          tacodevice = '//toftofsrv/toftof/rs232/ifchoppercontrol',
                          speed_accuracy = 2,
                          phase_accuracy = 10,
                          ch5_90deg_offset = 0),
    chWL         = device('nicos.toftof.chopper.Wavelength',
                          chopper = 'ch',
                          abslimits = (0.2, 16.0)),
    chSpeed      = device('nicos.toftof.chopper.Speed',
                          chopper = 'ch',
                          abslimits = (0, 22000.)),
    chRatio      = device('nicos.toftof.chopper.Ratio',
                          chopper = 'ch'),
    chCRC        = device('nicos.toftof.chopper.CRC',
                          chopper = 'ch'),
    chST         = device('nicos.toftof.chopper.SlitType',
                          chopper = 'ch'),
    chDS         = device('nicos.toftof.chopper.SpeedReadout',
                          chopper = 'ch',
                          fmtstr = '[%7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f]'),
)
