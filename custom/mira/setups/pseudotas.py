includes = ['base', 'mono2', 'detector', 'analyzer']

devices = dict(
    Sample = device('nicos.tas.TASSample'),

    mira   = device('nicos.tas.TAS',
                    instrument = 'MIRA',
                    responsible = 'Robert Georgii <robert.georgii@frm2.tum.de>',
                    axiscoupling = False,
                    psi360 = False,
                    cell = 'Sample',
                    phi = 'phi',
                    psi = 'om',
                    mono = 'mono',
                    ana = 'ana',
                    scatteringsense = (-1, 1, -1)),

    mono   = device('nicos.tas.Monochromator',
                    unit = 'A-1',
                    theta = 'vmth',
                    twotheta = 'vmtt',
                    focush = None,
                    focusv = None,
                    abslimits = (0, 10),
                    dvalue = 3.325),

    ana    = device('nicos.tas.Monochromator',
                    unit = 'A-1',
                    theta = 'vath',
                    twotheta = 'vatt',
                    focush = None,
                    focusv = None,
                    abslimits = (0, 10),
                    dvalue = 3.325),

    vmth   = device('nicos.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-360, 360)),

    vmtt   = device('nicos.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-360, 360)),

    vath   = device('nicos.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-360, 360)),

    vatt   = device('nicos.generic.VirtualMotor',
                    unit = 'deg',
                    abslimits = (-360, 360)),

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

