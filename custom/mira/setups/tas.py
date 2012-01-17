description = 'MIRA triple-axis setup'

includes = ['base', 'mono2', 'analyzer', 'detector']

devices = dict(
    Sample = device('nicos.tas.TASSample'),

    mira   = device('nicos.tas.TAS',
                    instrument = 'MIRA',
                    responsible = 'Robert Georgii <robert.georgii@frm2.tum.de>',
                    cell = 'Sample',
                    phi = 'phi',
                    psi = 'om',
                    mono = 'mono',
                    ana = 'ana',
                    scatteringsense = (-1, 1, -1)),

    vom    = device('nicos.generic.VirtualMotor',
                    abslimits = (-360, 360),
                    unit = 'deg'),

    mono   = device('nicos.tas.Monochromator',
                    unit = 'A-1',
                    theta = 'm2th',
                    twotheta = 'm2tt',
                    focush = None,
                    focusv = None,
                    abslimits = (0, 10),
                    dvalue = 3.325),

    ana    = device('nicos.tas.Monochromator',
                    unit = 'A-1',
                    theta = 'ath',
                    twotheta = 'att',
                    focush = None,
                    focusv = None,
                    abslimits = (0, 10),
                    dvalue = 3.325),

    ki     = device('nicos.tas.Wavevector',
                    unit = 'A-1',
                    base = 'mono',
                    tas = 'mira',
                    scanmode = 'CKI',
                    abslimits = (0, 10)),

    kf     = device('nicos.tas.Wavevector',
                    unit = 'A-1',
                    base = 'ana',
                    tas = 'mira',
                    scanmode = 'CKF',
                    abslimits = (0, 10)),
)

startupcode = '''
#SetDetectors(det)
'''
