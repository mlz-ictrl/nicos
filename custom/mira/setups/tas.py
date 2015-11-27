description = 'MIRA triple-axis setup'
group = 'basic'

includes = ['base', 'mono2', 'analyzer', 'detector', 'alias_sth']

modules = ['commands.tas']

devices = dict(
    Sample = device('devices.tas.TASSample',
                    description = 'sample object',
                   ),

    mira   = device('devices.tas.TAS',
                    description = 'instrument, moves in HKL space',
                    instrument = 'MIRA',
                    responsible = 'Robert Georgii <robert.georgii@frm2.tum.de>',
                    cell = 'Sample',
                    phi = 'phi',
                    psi = 'sth',
                    mono = 'mono',
                    ana = 'ana',
                    alpha = None,
                    scatteringsense = (-1, 1, -1),
                    axiscoupling = False,
                    psi360 = False,
                   ),

    ki     = device('devices.tas.Wavevector',
                    description = 'incoming wavevector, also sets constant-ki mode when moved',
                    unit = 'A-1',
                    base = 'mono',
                    tas = 'mira',
                    scanmode = 'CKI',
                   ),

    kf     = device('devices.tas.Wavevector',
                    description = 'outgoing wavevector, also sets constant-kf mode when moved',
                    unit = 'A-1',
                    base = 'ana',
                    tas = 'mira',
                    scanmode = 'CKF',
                   ),

    Ei     = device('devices.tas.Energy',
                    description = 'incoming energy, also sets constant-ki mode when moved',
                    unit = 'meV',
                    base = 'mono',
                    tas = 'mira',
                    scanmode = 'CKI',
                   ),

    Ef     = device('devices.tas.Energy',
                    description = 'outgoing energy, also sets constant-kf mode when moved',
                    unit = 'meV',
                    base = 'ana',
                    tas = 'mira',
                    scanmode = 'CKF',
                   ),
)

startupcode = '''
#SetDetectors(det)
'''
