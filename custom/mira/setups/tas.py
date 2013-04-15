description = 'MIRA triple-axis setup'
group = 'basic'

includes = ['base', 'mono2', 'analyzer', 'detector']

modules = ['nicos.commands.tas']

devices = dict(
    Sample = device('devices.tas.TASSample'),

    mira   = device('devices.tas.TAS',
                    instrument = 'MIRA',
                    responsible = 'Robert Georgii <robert.georgii@frm2.tum.de>',
                    cell = 'Sample',
                    phi = 'phi',
                    psi = 'om',
                    mono = 'mono',
                    ana = 'ana',
                    alpha = None,
                    scatteringsense = (-1, 1, -1),
                    axiscoupling = False,
                    psi360 = False),

    vom    = device('devices.generic.VirtualMotor',
                    abslimits = (-360, 360),
                    unit = 'deg'),

    ki     = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'mono',
                    tas = 'mira',
                    scanmode = 'CKI'),

    kf     = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'ana',
                    tas = 'mira',
                    scanmode = 'CKF'),

    Ei     = device('devices.tas.Energy',
                    unit = 'meV',
                    base = 'mono',
                    tas = 'mira',
                    scanmode = 'CKI'),

    Ef     = device('devices.tas.Energy',
                    unit = 'meV',
                    base = 'ana',
                    tas = 'mira',
                    scanmode = 'CKF'),
)

startupcode = '''
#SetDetectors(det)
'''
