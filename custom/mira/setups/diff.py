description = 'MIRA2 diffraction setup'
group = 'basic'

includes = ['base', 'mono2', 'detector', 'alias_sth']

modules = ['nicos.commands.tas']

devices = dict(
    Sample = device('devices.tas.TASSample'),

    mira   = device('devices.tas.TAS',
                    instrument = 'MIRA',
                    responsible = 'Robert Georgii <robert.georgii@frm2.tum.de>',
                    cell = 'Sample',
                    phi = 'phi',
                    psi = 'sth',
                    mono = 'mono',
                    ana = 'vana',
                    alpha = None,
                    scatteringsense = (-1, 1, -1),
                    axiscoupling = False,
                    psi360 = False,
                   ),

    vana      = device('devices.tas.Monochromator',
                       description = 'virtual analyzer',
                       unit = 'A-1',
                       dvalue = 3.355,
                       theta = 'vath',
                       twotheta = 'vatt',
                       focush = None,
                       focusv = None,
                       abslimits = (0.1, 10),
                      ),

    vath      = device('devices.generic.VirtualMotor',
                       unit = 'deg',
                       abslimits = (-180, 180),
                       precision = 0.05,
                      ),

    vatt      = device('devices.generic.VirtualMotor',
                       unit = 'deg',
                       abslimits = (-180, 180),
                       precision = 0.05,
                      ),

    ki     = device('devices.tas.Wavevector',
                    unit = 'A-1',
                    base = 'mono',
                    tas = 'mira',
                    scanmode = 'CKI',
                   ),

    Ei     = device('devices.tas.Energy',
                    unit = 'meV',
                    base = 'mono',
                    tas = 'mira',
                    scanmode = 'CKI',
                   ),

    lam    = device('devices.tas.Wavelength',
                    unit = 'AA',
                    base = 'mono',
                    tas = 'mira',
                    scanmode = 'CKI',
                   ),
)

startupcode = '''
#SetDetectors(det)
'''
