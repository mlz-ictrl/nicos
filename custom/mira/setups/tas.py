description = 'MIRA triple-axis setup'
group = 'basic'

includes = ['base', 'mono2', 'analyzer', 'detector']

modules = ['nicos.commands.tas']

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
